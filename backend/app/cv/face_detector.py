from abc import ABC, abstractmethod
import numpy as np

class DetectedFace:
    """Represents a detected face in an image."""
    def __init__(self, bbox: tuple[int, int, int, int], confidence: float, 
                 landmarks: np.ndarray | None = None, aligned_face: np.ndarray | None = None):
        self.bbox = bbox  # (x, y, w, h)
        self.confidence = confidence
        self.landmarks = landmarks
        self.aligned_face = aligned_face

class FaceDetector(ABC):
    @abstractmethod
    def detect_faces(self, image: np.ndarray, min_confidence: float = 0.5) -> list[DetectedFace]:
        pass
    
    @abstractmethod  
    def detect_single_face(self, image: np.ndarray, min_confidence: float = 0.5) -> DetectedFace | None:
        """Detect exactly one face. Returns None if 0 or >1 faces detected."""
        pass

class OpenCVFaceDetector(FaceDetector):
    """
    Face detector using OpenCV's DNN module with a pre-trained Caffe SSD model.
    Falls back to Haar Cascade if the DNN model files are not available.
    """
    def __init__(self):
        # Try to use OpenCV's DNN face detector (more accurate)
        # If model files aren't available, fall back to Haar cascade
        import cv2
        self._use_dnn = False
        self._net = None
        self._cascade = None
        
        # Try DNN first
        try:
            # Use OpenCV's built-in face detection DNN if available
            prototxt_path = cv2.data.haarcascades  # check if cv2.data exists
            # Actually, for DNN we need the model files. Let's check for them
            # in a known location
            import os
            model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
            prototxt = os.path.join(model_dir, 'deploy.prototxt')
            caffemodel = os.path.join(model_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
            
            if os.path.exists(prototxt) and os.path.exists(caffemodel):
                self._net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
                self._use_dnn = True
        except Exception:
            pass
        
        if not self._use_dnn:
            # Fall back to Haar Cascade (ships with OpenCV)
            self._cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
    
    def detect_faces(self, image: np.ndarray, min_confidence: float = 0.5) -> list[DetectedFace]:
        import cv2
        faces = []
        h, w = image.shape[:2]
        
        if self._use_dnn and self._net is not None:
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 1.0, (300, 300),
                (104.0, 177.0, 123.0), swapRB=False, crop=False
            )
            self._net.setInput(blob)
            detections = self._net.forward()
            
            for i in range(detections.shape[2]):
                confidence = float(detections[0, 0, i, 2])
                if confidence >= min_confidence:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    x1, y1, x2, y2 = box.astype(int)
                    # Clamp to image bounds
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(w, x2)
                    y2 = min(h, y2)
                    bw, bh = x2 - x1, y2 - y1
                    if bw > 20 and bh > 20:  # minimum face size
                        face_roi = image[y1:y2, x1:x2]
                        faces.append(DetectedFace(
                            bbox=(x1, y1, bw, bh),
                            confidence=confidence,
                            aligned_face=face_roi
                        ))
        else:
            # Haar Cascade fallback
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            rects = self._cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            for (x, y, bw, bh) in rects:
                face_roi = image[y:y+bh, x:x+bw]
                faces.append(DetectedFace(
                    bbox=(x, y, bw, bh),
                    confidence=0.9,  # Haar doesn't give confidence
                    aligned_face=face_roi
                ))
        
        return faces
    
    def detect_single_face(self, image: np.ndarray, min_confidence: float = 0.5) -> DetectedFace | None:
        faces = self.detect_faces(image, min_confidence)
        if len(faces) == 1:
            return faces[0]
        return None
