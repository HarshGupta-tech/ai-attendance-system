import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class QualityResult:
    is_acceptable: bool
    blur_score: float  # higher = sharper, threshold ~100
    brightness: float  # 0-255, ideal 80-200
    face_size_ratio: float  # face area / image area, should be > 0.05
    issues: list[str]

class ImageQualityChecker:
    """Checks image quality for face registration."""
    
    def __init__(self, min_blur_score: float = 80.0, 
                 min_brightness: float = 40.0,
                 max_brightness: float = 220.0,
                 min_face_ratio: float = 0.03):
        self.min_blur_score = min_blur_score
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_face_ratio = min_face_ratio
    
    def check_quality(self, image: np.ndarray, face_bbox: tuple[int, int, int, int] | None = None) -> QualityResult:
        issues = []
        
        # Check blur using Laplacian variance
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur_score < self.min_blur_score:
            issues.append(f"Image is too blurry (score: {blur_score:.1f}, min: {self.min_blur_score})")
        
        # Check brightness
        brightness = np.mean(gray)
        if brightness < self.min_brightness:
            issues.append(f"Image is too dark (brightness: {brightness:.1f})")
        elif brightness > self.max_brightness:
            issues.append(f"Image is too bright (brightness: {brightness:.1f})")
        
        # Check face size ratio
        face_size_ratio = 0.0
        if face_bbox:
            x, y, w, h = face_bbox
            img_h, img_w = image.shape[:2]
            face_area = w * h
            img_area = img_w * img_h
            face_size_ratio = face_area / img_area if img_area > 0 else 0
            if face_size_ratio < self.min_face_ratio:
                issues.append(f"Face is too small (ratio: {face_size_ratio:.3f}, min: {self.min_face_ratio})")
        
        # Check image resolution
        h, w = image.shape[:2]
        if w < 200 or h < 200:
            issues.append(f"Image resolution too low ({w}x{h})")
        
        return QualityResult(
            is_acceptable=len(issues) == 0,
            blur_score=blur_score,
            brightness=brightness,
            face_size_ratio=face_size_ratio,
            issues=issues
        )
    
    def compute_overall_quality(self, image: np.ndarray, face_bbox: tuple[int, int, int, int] | None = None) -> float:
        """Returns a quality score from 0 to 1."""
        result = self.check_quality(image, face_bbox)
        
        # Normalize each metric to 0-1
        blur_norm = min(result.blur_score / 300.0, 1.0)
        bright_norm = 1.0 - abs(result.brightness - 130.0) / 130.0
        bright_norm = max(0.0, bright_norm)
        size_norm = min(result.face_size_ratio / 0.15, 1.0) if face_bbox else 0.5
        
        # Weighted average
        score = 0.4 * blur_norm + 0.3 * bright_norm + 0.3 * size_norm
        return round(max(0.0, min(1.0, score)), 3)
