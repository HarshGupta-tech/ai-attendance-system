from abc import ABC, abstractmethod
import numpy as np
import logging
import json

logger = logging.getLogger(__name__)

class FaceEncoder(ABC):
    """Abstract base class for face encoding."""
    
    @abstractmethod
    def encode_face(self, face_image: np.ndarray) -> np.ndarray | None:
        """Generate a face embedding from a face image. Returns 128-d vector or None."""
        pass
    
    @abstractmethod
    def encode_faces(self, face_images: list[np.ndarray]) -> list[np.ndarray]:
        """Generate embeddings for multiple face images."""
        pass
    
    def embedding_to_json(self, embedding: np.ndarray) -> str:
        """Serialize embedding to JSON string for storage."""
        return json.dumps(embedding.tolist())
    
    def embedding_from_json(self, json_str: str) -> np.ndarray:
        """Deserialize embedding from JSON string."""
        return np.array(json.loads(json_str))
    
    def embeddings_to_json(self, embeddings: list[np.ndarray]) -> str:
        """Serialize list of embeddings to JSON string."""
        return json.dumps([e.tolist() for e in embeddings])
    
    def embeddings_from_json(self, json_str: str) -> list[np.ndarray]:
        """Deserialize list of embeddings from JSON string."""
        data = json.loads(json_str)
        return [np.array(e) for e in data]


class DlibFaceEncoder(FaceEncoder):
    """
    Face encoder using the face_recognition library (dlib-based).
    Generates 128-dimensional face embeddings.
    """
    
    def __init__(self):
        self._available = False
        try:
            import face_recognition
            self._fr = face_recognition
            self._available = True
            logger.info("DlibFaceEncoder initialized successfully")
        except ImportError:
            logger.warning(
                "face_recognition library not available. "
                "Install with: pip install face_recognition. "
                "Falling back to demo encoder."
            )
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    def encode_face(self, face_image: np.ndarray) -> np.ndarray | None:
        if not self._available:
            return None
        try:
            import cv2
            # face_recognition expects RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            # Get face encodings
            encodings = self._fr.face_encodings(rgb_image)
            if encodings:
                return encodings[0]
            # If no face found in the crop, try with the full image and known location
            h, w = rgb_image.shape[:2]
            face_locations = [(0, w, h, 0)]  # top, right, bottom, left
            encodings = self._fr.face_encodings(rgb_image, known_face_locations=face_locations)
            if encodings:
                return encodings[0]
            return None
        except Exception as e:
            logger.error(f"Face encoding failed: {e}")
            return None
    
    def encode_faces(self, face_images: list[np.ndarray]) -> list[np.ndarray]:
        encodings = []
        for img in face_images:
            enc = self.encode_face(img)
            if enc is not None:
                encodings.append(enc)
        return encodings


class DemoFaceEncoder(FaceEncoder):
    """
    Demo/fallback face encoder that generates deterministic pseudo-embeddings.
    Uses image statistics to create reproducible 128-d vectors.
    NOT suitable for real recognition — only for demo/testing when dlib is unavailable.
    """
    
    def __init__(self):
        logger.warning("Using DemoFaceEncoder — recognition accuracy will be limited")
    
    @property
    def is_available(self) -> bool:
        return True
    
    def encode_face(self, face_image: np.ndarray) -> np.ndarray | None:
        try:
            import cv2
            # Resize to consistent size
            resized = cv2.resize(face_image, (64, 64))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(resized.shape) == 3 else resized
            
            # Use image statistics + histogram to create a pseudo-embedding
            hist = cv2.calcHist([gray], [0], None, [64], [0, 256]).flatten()
            hist = hist / (np.linalg.norm(hist) + 1e-7)
            
            # Add spatial features
            blocks = []
            for i in range(0, 64, 16):
                for j in range(0, 64, 16):
                    block = gray[i:i+16, j:j+16]
                    blocks.extend([np.mean(block) / 255.0, np.std(block) / 128.0])
            
            spatial = np.array(blocks[:32])
            
            # LBP-like features
            lbp_features = []
            for i in range(1, gray.shape[0]-1, 8):
                for j in range(1, gray.shape[1]-1, 8):
                    center = float(gray[i, j])
                    neighbors = [
                        float(gray[i-1, j]), float(gray[i+1, j]),
                        float(gray[i, j-1]), float(gray[i, j+1])
                    ]
                    pattern = sum(1 << k for k, n in enumerate(neighbors) if n >= center)
                    lbp_features.append(pattern / 16.0)
            
            lbp_arr = np.array(lbp_features[:32])
            
            # Concatenate to 128-d
            embedding = np.concatenate([hist, spatial, lbp_arr])
            # Pad or truncate to exactly 128
            if len(embedding) < 128:
                embedding = np.pad(embedding, (0, 128 - len(embedding)))
            else:
                embedding = embedding[:128]
            
            # L2 normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            return embedding
        except Exception as e:
            logger.error(f"Demo face encoding failed: {e}")
            return None
    
    def encode_faces(self, face_images: list[np.ndarray]) -> list[np.ndarray]:
        encodings = []
        for img in face_images:
            enc = self.encode_face(img)
            if enc is not None:
                encodings.append(enc)
        return encodings


class DeepFaceEncoder(FaceEncoder):
    """
    High-accuracy face encoder using the DeepFace library.
    Generates embeddings (e.g., 128-d for Facenet or 2622-d for VGG-Face).
    """
    
    def __init__(self):
        self._available = False
        try:
            from deepface import DeepFace
            self._df = DeepFace
            self._available = True
            logger.info("DeepFaceEncoder initialized successfully")
        except Exception as e:
            logger.warning(f"DeepFace library not available or failed to initialize: {e}")
            
    @property
    def is_available(self) -> bool:
        return self._available
        
    def encode_face(self, face_image: np.ndarray) -> np.ndarray | None:
        if not self.is_available:
            return None
            
        try:
            # DeepFace expects BGR image (OpenCV default)
            # Provide enforce_detection=False since we already cropped the face
            embedding_objs = self._df.represent(
                img_path=face_image,
                model_name="Facenet",
                enforce_detection=False
            )
            if embedding_objs and len(embedding_objs) > 0:
                # Returns a list of dicts, take the first one
                embedding = np.array(embedding_objs[0]['embedding'])
                
                # L2 Normalize the embedding for cosine distance comparison
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                return embedding
            return None
        except Exception as e:
            logger.error(f"DeepFace encoder error: {e}")
            return None
            
    def encode_faces(self, face_images: list[np.ndarray]) -> list[np.ndarray]:
        encodings = []
        for img in face_images:
            enc = self.encode_face(img)
            if enc is not None:
                encodings.append(enc)
        return encodings


def get_face_encoder() -> FaceEncoder:
    """Factory function to get the best available face encoder."""
    
    # 1. Try Dlib (fastest, requires C++ compilation)
    encoder = DlibFaceEncoder()
    if encoder.is_available:
        return encoder
        
    # 2. Try DeepFace (high accuracy, uses TensorFlow/PyTorch)
    df_encoder = DeepFaceEncoder()
    if df_encoder.is_available:
        return df_encoder
        
    # 3. Fallback to Demo Encoder (pixel statistics, low accuracy)
    logger.warning("Falling back to DemoFaceEncoder")
    return DemoFaceEncoder()
