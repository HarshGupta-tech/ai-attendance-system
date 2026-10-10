import numpy as np
import pytest

def test_face_detector_initialization():
    from app.cv.face_detector import OpenCVFaceDetector
    detector = OpenCVFaceDetector()
    assert detector is not None

def test_face_detector_no_face():
    from app.cv.face_detector import OpenCVFaceDetector
    detector = OpenCVFaceDetector()
    # Create a blank image (no face)
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    faces = detector.detect_faces(blank)
    assert len(faces) == 0

def test_face_detector_single_face():
    from app.cv.face_detector import OpenCVFaceDetector
    detector = OpenCVFaceDetector()
    # Create a simple test image with a face-like pattern
    # (This may not detect in Haar cascade, but tests the interface)
    img = np.random.randint(100, 200, (480, 640, 3), dtype=np.uint8)
    faces = detector.detect_faces(img, min_confidence=0.3)
    # Just verify it returns a list (may be empty without a real face)
    assert isinstance(faces, list)

def test_image_quality_checker():
    from app.cv.image_quality import ImageQualityChecker
    checker = ImageQualityChecker()
    
    # Good quality image (random with texture)
    good_img = np.random.randint(60, 200, (480, 640, 3), dtype=np.uint8)
    result = checker.check_quality(good_img, (100, 100, 200, 200))
    assert result.blur_score > 0
    assert 0 <= result.brightness <= 255

def test_image_quality_blurry():
    from app.cv.image_quality import ImageQualityChecker
    checker = ImageQualityChecker()
    
    # Blurry image (uniform color)
    blurry = np.ones((480, 640, 3), dtype=np.uint8) * 128
    result = checker.check_quality(blurry, (100, 100, 200, 200))
    assert result.blur_score < 100  # Should be detected as blurry

def test_image_quality_dark():
    from app.cv.image_quality import ImageQualityChecker
    checker = ImageQualityChecker()
    
    dark = np.zeros((480, 640, 3), dtype=np.uint8) + 10
    result = checker.check_quality(dark)
    assert "dark" in " ".join(result.issues).lower() or result.brightness < 40

def test_face_encoder_demo():
    from app.ml.face_encoder import DemoFaceEncoder
    encoder = DemoFaceEncoder()
    assert encoder.is_available
    
    # Create a test face image
    face_img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    embedding = encoder.encode_face(face_img)
    assert embedding is not None
    assert len(embedding) == 128
    assert abs(np.linalg.norm(embedding) - 1.0) < 0.01  # Should be L2 normalized

def test_face_encoder_consistency():
    from app.ml.face_encoder import DemoFaceEncoder
    encoder = DemoFaceEncoder()
    
    # Same image should produce similar embeddings
    face_img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    emb1 = encoder.encode_face(face_img)
    emb2 = encoder.encode_face(face_img)
    assert emb1 is not None and emb2 is not None
    distance = np.linalg.norm(emb1 - emb2)
    assert distance < 0.01  # Same image = same embedding

def test_face_matcher():
    from app.ml.face_matcher import FaceMatcher
    matcher = FaceMatcher(threshold=0.6)
    
    # Create known embedding
    known_emb = np.random.randn(128).astype(np.float64)
    known_emb /= np.linalg.norm(known_emb)
    
    matcher.add_embedding(1, "S001", "Test Student", [known_emb])
    
    # Match with same embedding (should match)
    result = matcher.match_face(known_emb)
    assert result.matched
    assert result.student_id == "S001"
    assert result.distance < 0.01

def test_face_matcher_unknown():
    from app.ml.face_matcher import FaceMatcher
    matcher = FaceMatcher(threshold=0.6)
    
    known_emb = np.random.randn(128).astype(np.float64)
    known_emb /= np.linalg.norm(known_emb)
    matcher.add_embedding(1, "S001", "Test Student", [known_emb])
    
    # Unknown face (very different embedding)
    unknown_emb = -known_emb  # Opposite direction
    result = matcher.match_face(unknown_emb)
    assert not result.matched

def test_face_matcher_threshold():
    from app.ml.face_matcher import FaceMatcher
    
    known_emb = np.random.randn(128).astype(np.float64)
    known_emb /= np.linalg.norm(known_emb)
    
    # Strict threshold
    matcher_strict = FaceMatcher(threshold=0.1)
    matcher_strict.add_embedding(1, "S001", "Test", [known_emb])
    
    # Slightly different embedding
    noise = np.random.randn(128) * 0.1
    query = known_emb + noise
    query /= np.linalg.norm(query)
    
    result_strict = matcher_strict.match_face(query)
    
    # Lenient threshold
    matcher_lenient = FaceMatcher(threshold=1.0)
    matcher_lenient.add_embedding(1, "S001", "Test", [known_emb])
    result_lenient = matcher_lenient.match_face(query)
    
    # Lenient should match if strict doesn't
    if not result_strict.matched:
        assert result_lenient.matched

def test_face_encoder_serialization():
    from app.ml.face_encoder import DemoFaceEncoder
    encoder = DemoFaceEncoder()
    
    face_img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    embedding = encoder.encode_face(face_img)
    assert embedding is not None
    
    # Test serialization
    json_str = encoder.embedding_to_json(embedding)
    restored = encoder.embedding_from_json(json_str)
    assert np.allclose(embedding, restored)

def test_liveness_detector():
    from app.ml.liveness import LivenessDetector
    detector = LivenessDetector()
    detector.reset()
    
    # Process a few frames
    for i in range(15):
        face_img = np.random.randint(50, 200, (200, 200, 3), dtype=np.uint8)
        result = detector.check_frame(face_img, (0, 0, 200, 200))
        assert hasattr(result, 'is_live')
        assert hasattr(result, 'checks_passed')

def test_base64_image_conversion():
    from app.cv.camera import encode_image_base64, decode_base64_image
    
    # Create test image
    original = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Encode and decode
    b64 = encode_image_base64(original)
    decoded = decode_base64_image(b64)
    assert decoded is not None
    assert decoded.shape[0] > 0 and decoded.shape[1] > 0

def test_recognition_pipeline_initialization():
    from app.ml.recognition_pipeline import RecognitionPipeline
    pipeline = RecognitionPipeline(threshold=0.6, enable_liveness=False)
    assert pipeline.detector is not None
    assert pipeline.encoder is not None
    assert pipeline.matcher is not None

def test_evaluation_metrics():
    from app.ml.evaluation import EvaluationMetrics
    metrics = EvaluationMetrics(
        true_positives=80,
        true_negatives=15,
        false_positives=3,
        false_negatives=2,
        total_tests=100
    )
    total = metrics.true_positives + metrics.true_negatives + metrics.false_positives + metrics.false_negatives
    accuracy = (metrics.true_positives + metrics.true_negatives) / total
    assert accuracy > 0.9
