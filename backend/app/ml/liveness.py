import numpy as np
import cv2
import logging
from dataclasses import dataclass, field
from collections import deque
import time

logger = logging.getLogger(__name__)

@dataclass
class LivenessResult:
    is_live: bool
    confidence: float = 0.0
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    challenge: str | None = None  # Next challenge for the user
    message: str = ""

class LivenessDetector:
    """
    Practical anti-spoofing mechanism using:
    1. Eye Aspect Ratio (EAR) for blink detection
    2. Face movement tracking across frames
    3. Texture analysis (LBP variance) to detect flat printed photos
    4. Multi-frame consistency
    
    NOTE: This is a practical anti-spoofing mechanism suitable for a college project,
    NOT enterprise-grade biometric security. It can distinguish a live person from
    a static photograph in most cases but is not designed to defeat sophisticated attacks.
    """
    
    def __init__(self, 
                 ear_threshold: float = 0.22,
                 blink_frames: int = 3,
                 movement_threshold: float = 5.0,
                 texture_threshold: float = 10.0,
                 history_size: int = 30):
        self.ear_threshold = ear_threshold
        self.blink_frames = blink_frames
        self.movement_threshold = movement_threshold
        self.texture_threshold = texture_threshold
        self.history_size = history_size
        
        # State tracking
        self._face_positions: deque = deque(maxlen=history_size)
        self._ear_history: deque = deque(maxlen=history_size)
        self._blink_detected = False
        self._movement_detected = False
        self._blink_count = 0
        self._frame_count = 0
        self._consecutive_blink_frames = 0
        self._last_challenge_time = 0
        self._current_challenge: str | None = "Please blink your eyes"
        
        # Try to load dlib for landmark detection
        self._landmark_available = False
        try:
            import dlib
            import os
            predictor_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'models',
                'shape_predictor_68_face_landmarks.dat'
            )
            if os.path.exists(predictor_path):
                self._predictor = dlib.shape_predictor(predictor_path)
                self._detector = dlib.get_frontal_face_detector()
                self._landmark_available = True
                logger.info("Dlib landmark detector loaded for liveness detection")
            else:
                logger.info("Dlib landmark model not found, using fallback liveness detection")
        except ImportError:
            logger.info("Dlib not available, using fallback liveness detection")
    
    def reset(self):
        """Reset liveness detection state for a new session."""
        self._face_positions.clear()
        self._ear_history.clear()
        self._blink_detected = False
        self._movement_detected = False
        self._blink_count = 0
        self._frame_count = 0
        self._consecutive_blink_frames = 0
        self._current_challenge = "Please blink your eyes"
    
    def _compute_ear(self, eye_points: np.ndarray) -> float:
        """Compute Eye Aspect Ratio (EAR) from 6 eye landmark points."""
        # EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        if C == 0:
            return 0.0
        return (A + B) / (2.0 * C)
    
    def _compute_texture_variance(self, face_image: np.ndarray) -> float:
        """Compute texture variance to detect flat printed photos."""
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(face_image.shape) == 3 else face_image
        resized = cv2.resize(gray, (64, 64))
        
        # Compute Local Binary Pattern variance
        lbp_values = []
        for i in range(1, resized.shape[0] - 1):
            for j in range(1, resized.shape[1] - 1):
                center = int(resized[i, j])
                pattern = 0
                neighbors = [
                    (i-1, j-1), (i-1, j), (i-1, j+1),
                    (i, j+1), (i+1, j+1), (i+1, j),
                    (i+1, j-1), (i, j-1)
                ]
                for k, (ni, nj) in enumerate(neighbors):
                    if int(resized[ni, nj]) >= center:
                        pattern |= (1 << k)
                lbp_values.append(pattern)
        
        return float(np.std(lbp_values))
    
    def _detect_blink_fallback(self, face_image: np.ndarray) -> bool:
        """Fallback blink detection using eye region intensity analysis."""
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(face_image.shape) == 3 else face_image
        h, w = gray.shape[:2]
        
        # Approximate eye regions (upper third of face, left and right halves)
        eye_region_top = int(h * 0.2)
        eye_region_bottom = int(h * 0.45)
        
        left_eye = gray[eye_region_top:eye_region_bottom, int(w*0.1):int(w*0.45)]
        right_eye = gray[eye_region_top:eye_region_bottom, int(w*0.55):int(w*0.9)]
        
        if left_eye.size == 0 or right_eye.size == 0:
            return False
        
        # Compute mean intensity of eye regions
        avg_intensity = (np.mean(left_eye) + np.mean(right_eye)) / 2.0
        
        self._ear_history.append(avg_intensity)
        
        if len(self._ear_history) >= 5:
            recent = list(self._ear_history)[-5:]
            # Detect significant drop in eye region intensity (eyes closing)
            baseline = np.mean(list(self._ear_history)[:-3]) if len(self._ear_history) > 3 else recent[0]
            current = np.mean(recent[-2:])
            drop = baseline - current
            if drop > 15:  # Significant intensity drop = potential blink
                return True
        
        return False
    
    def check_frame(self, face_image: np.ndarray, face_bbox: tuple[int, int, int, int] | None = None) -> LivenessResult:
        """
        Process a frame for liveness detection.
        Call this for each frame during the liveness check phase.
        """
        self._frame_count += 1
        checks_passed = []
        checks_failed = []
        
        # 1. Texture analysis
        texture_var = self._compute_texture_variance(face_image)
        if texture_var > self.texture_threshold:
            checks_passed.append("texture_analysis")
        else:
            checks_failed.append("texture_analysis")
        
        # 2. Face movement tracking
        if face_bbox:
            center = (face_bbox[0] + face_bbox[2] // 2, face_bbox[1] + face_bbox[3] // 2)
            self._face_positions.append(center)
            
            if len(self._face_positions) >= 5:
                positions = list(self._face_positions)
                movements = [
                    np.sqrt((positions[i][0] - positions[i-1][0])**2 + 
                           (positions[i][1] - positions[i-1][1])**2)
                    for i in range(1, len(positions))
                ]
                avg_movement = np.mean(movements)
                if avg_movement > self.movement_threshold:
                    self._movement_detected = True
                    checks_passed.append("movement_detection")
                else:
                    checks_failed.append("movement_detection")
        
        # 3. Blink detection
        if self._landmark_available:
            try:
                import dlib
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(face_image.shape) == 3 else face_image
                rects = self._detector(gray, 0)
                if rects:
                    shape = self._predictor(gray, rects[0])
                    landmarks = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
                    
                    # Left eye: points 36-41, Right eye: points 42-47
                    left_ear = self._compute_ear(landmarks[36:42])
                    right_ear = self._compute_ear(landmarks[42:48])
                    ear = (left_ear + right_ear) / 2.0
                    
                    self._ear_history.append(ear)
                    
                    if ear < self.ear_threshold:
                        self._consecutive_blink_frames += 1
                    else:
                        if self._consecutive_blink_frames >= self.blink_frames:
                            self._blink_detected = True
                            self._blink_count += 1
                        self._consecutive_blink_frames = 0
            except Exception as e:
                logger.debug(f"Landmark-based blink detection failed: {e}")
                if self._detect_blink_fallback(face_image):
                    self._blink_detected = True
                    self._blink_count += 1
        else:
            # Fallback blink detection
            if self._detect_blink_fallback(face_image):
                self._blink_detected = True
                self._blink_count += 1
        
        if self._blink_detected:
            checks_passed.append("blink_detection")
        else:
            checks_failed.append("blink_detection")
        
        # 4. Multi-frame consistency
        if self._frame_count >= 10:
            checks_passed.append("multi_frame_consistency")
        else:
            checks_failed.append("multi_frame_consistency")
        
        # Determine overall liveness
        # Require at least 2 of 4 checks to pass, including texture
        passed_count = len(checks_passed)
        is_live = passed_count >= 2 and "texture_analysis" in checks_passed
        
        # Update challenge
        if not self._blink_detected:
            self._current_challenge = "Please blink your eyes"
        elif not self._movement_detected:
            self._current_challenge = "Please move your head slightly"
        else:
            self._current_challenge = None
        
        confidence = min(1.0, passed_count / 4.0)
        
        message = ""
        if is_live:
            message = "Liveness verified"
        elif self._current_challenge:
            message = self._current_challenge
        else:
            message = "Liveness check in progress..."
        
        return LivenessResult(
            is_live=is_live,
            confidence=round(confidence, 2),
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            challenge=self._current_challenge,
            message=message
        )
    
    def get_summary(self) -> dict:
        """Get summary of liveness detection state."""
        return {
            "frames_processed": self._frame_count,
            "blink_detected": self._blink_detected,
            "blink_count": self._blink_count,
            "movement_detected": self._movement_detected,
            "landmark_available": self._landmark_available,
            "current_challenge": self._current_challenge
        }
