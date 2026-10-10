import numpy as np
import logging
import time
from dataclasses import dataclass, field

from app.cv.face_detector import FaceDetector, OpenCVFaceDetector, DetectedFace
from app.cv.image_quality import ImageQualityChecker, QualityResult
from app.cv.camera import decode_base64_image, resize_for_processing
from app.ml.face_encoder import FaceEncoder, get_face_encoder
from app.ml.face_matcher import FaceMatcher, MatchResult
from app.ml.liveness import LivenessDetector, LivenessResult

logger = logging.getLogger(__name__)

@dataclass
class RecognitionOutput:
    """Output of the recognition pipeline for a single face."""
    bbox: tuple[int, int, int, int]
    match: MatchResult
    quality: QualityResult | None = None
    liveness: LivenessResult | None = None

@dataclass 
class PipelineResult:
    """Full result from processing one frame."""
    faces: list[RecognitionOutput] = field(default_factory=list)
    processing_time_ms: float = 0.0
    frame_width: int = 0
    frame_height: int = 0
    error: str | None = None

class RecognitionPipeline:
    """
    Complete face recognition pipeline:
    Frame -> Detect -> Quality Check -> Encode -> Match -> (Optional Liveness) -> Result
    
    This pipeline is designed to be modular — each component (detector, encoder, matcher)
    can be swapped independently.
    """
    
    def __init__(self, 
                 threshold: float = 0.6,
                 enable_liveness: bool = False,
                 max_processing_width: int = 640):
        self.detector: FaceDetector = OpenCVFaceDetector()
        self.encoder: FaceEncoder = get_face_encoder()
        self.matcher: FaceMatcher = FaceMatcher(threshold=threshold)
        self.quality_checker: ImageQualityChecker = ImageQualityChecker()
        self.liveness_detector: LivenessDetector | None = LivenessDetector() if enable_liveness else None
        self.max_processing_width = max_processing_width
        
        logger.info(
            f"RecognitionPipeline initialized: "
            f"encoder={'dlib' if hasattr(self.encoder, '_fr') else 'demo'}, "
            f"threshold={threshold}, liveness={enable_liveness}"
        )
    
    def load_embeddings(self, embeddings_data: list[dict]):
        """Load known student embeddings for matching."""
        self.matcher.load_embeddings(embeddings_data)
    
    def process_frame(self, image: np.ndarray, check_liveness: bool = False) -> PipelineResult:
        """
        Process a single frame through the full pipeline.
        
        Args:
            image: BGR image (numpy array)
            check_liveness: Whether to perform liveness check
        
        Returns:
            PipelineResult with recognized faces
        """
        start_time = time.time()
        result = PipelineResult(
            frame_width=image.shape[1],
            frame_height=image.shape[0]
        )
        
        try:
            # 1. Resize for faster processing
            processed = resize_for_processing(image, self.max_processing_width)
            scale_x = image.shape[1] / processed.shape[1]
            scale_y = image.shape[0] / processed.shape[0]
            
            # 2. Detect faces
            detected_faces = self.detector.detect_faces(processed, min_confidence=0.5)
            
            if not detected_faces:
                result.processing_time_ms = (time.time() - start_time) * 1000
                return result
            
            # 3. Process each detected face
            for face in detected_faces:
                # Scale bounding box back to original size
                x, y, w, h = face.bbox
                original_bbox = (
                    int(x * scale_x), int(y * scale_y),
                    int(w * scale_x), int(h * scale_y)
                )
                
                # Extract face region from original image for better quality encoding
                ox, oy, ow, oh = original_bbox
                # Add margin
                margin = int(max(ow, oh) * 0.2)
                fx1 = max(0, ox - margin)
                fy1 = max(0, oy - margin)
                fx2 = min(image.shape[1], ox + ow + margin)
                fy2 = min(image.shape[0], oy + oh + margin)
                face_roi = image[fy1:fy2, fx1:fx2]
                
                if face_roi.size == 0:
                    continue
                
                # 4. Quality check
                quality = self.quality_checker.check_quality(face_roi, original_bbox)
                
                # 5. Generate embedding
                embedding = self.encoder.encode_face(face_roi)
                
                if embedding is None:
                    result.faces.append(RecognitionOutput(
                        bbox=original_bbox,
                        match=MatchResult(matched=False),
                        quality=quality
                    ))
                    continue
                
                # 6. Match against known embeddings
                match = self.matcher.match_face(embedding)
                
                # 7. Optional liveness check
                liveness = None
                if check_liveness and self.liveness_detector:
                    liveness = self.liveness_detector.check_frame(face_roi, original_bbox)
                
                result.faces.append(RecognitionOutput(
                    bbox=original_bbox,
                    match=match,
                    quality=quality,
                    liveness=liveness
                ))
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            result.error = str(e)
        
        result.processing_time_ms = round((time.time() - start_time) * 1000, 2)
        return result
    
    def process_base64_frame(self, base64_image: str, check_liveness: bool = False) -> PipelineResult:
        """Process a base64-encoded image frame."""
        image = decode_base64_image(base64_image)
        if image is None:
            return PipelineResult(error="Failed to decode image")
        return self.process_frame(image, check_liveness)
    
    def register_face(self, images: list[np.ndarray]) -> dict:
        """
        Process multiple images for face registration.
        Returns dict with encodings and quality info.
        """
        encodings = []
        quality_scores = []
        rejected = 0
        
        for img in images:
            # Detect face
            face = self.detector.detect_single_face(img)
            if face is None:
                rejected += 1
                continue
            
            # Check quality
            quality = self.quality_checker.check_quality(img, face.bbox)
            if not quality.is_acceptable:
                rejected += 1
                continue
            
            # Extract face region
            x, y, w, h = face.bbox
            margin = int(max(w, h) * 0.2)
            fx1 = max(0, x - margin)
            fy1 = max(0, y - margin)
            fx2 = min(img.shape[1], x + w + margin)
            fy2 = min(img.shape[0], y + h + margin)
            face_roi = img[fy1:fy2, fx1:fx2]
            
            # Generate encoding
            encoding = self.encoder.encode_face(face_roi)
            if encoding is not None:
                encodings.append(encoding)
                quality_scores.append(
                    self.quality_checker.compute_overall_quality(img, face.bbox)
                )
        
        avg_quality = float(np.mean(quality_scores)) if quality_scores else 0.0
        
        return {
            'success': len(encodings) >= 3,  # Need at least 3 good samples
            'encodings': encodings,
            'num_samples': len(encodings),
            'rejected': rejected,
            'quality_score': round(avg_quality, 3),
            'message': (
                f"Successfully encoded {len(encodings)} face samples"
                if len(encodings) >= 3
                else f"Need at least 3 face samples, got {len(encodings)}. "
                     f"{rejected} images were rejected."
            )
        }

# Singleton pipeline instance
_pipeline_instance: RecognitionPipeline | None = None

def get_pipeline(threshold: float = 0.6, enable_liveness: bool = False) -> RecognitionPipeline:
    """Get or create the recognition pipeline singleton."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RecognitionPipeline(
            threshold=threshold,
            enable_liveness=enable_liveness
        )
    return _pipeline_instance

def reset_pipeline():
    """Reset the pipeline singleton (useful for testing)."""
    global _pipeline_instance
    _pipeline_instance = None
