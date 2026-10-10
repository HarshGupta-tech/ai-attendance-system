import numpy as np
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    """Result of a face matching operation."""
    matched: bool
    student_db_id: int | None = None  # database ID
    student_id: str | None = None  # student ID string
    student_name: str | None = None
    distance: float = float('inf')
    confidence: float = 0.0

class FaceMatcher:
    """
    Matches face embeddings against a database of known embeddings.
    Uses Euclidean distance with a configurable threshold.
    """
    
    def __init__(self, threshold: float = 0.6, use_cosine: bool = False):
        self.threshold = threshold
        self.use_cosine = use_cosine
        self._known_embeddings: dict[int, dict] = {}  # student_db_id -> {embeddings, student_id, name}
        logger.info(f"FaceMatcher initialized with threshold={threshold}, metric={'cosine' if use_cosine else 'euclidean'}")
    
    def load_embeddings(self, embeddings_data: list[dict]):
        """
        Load known embeddings from database.
        Each dict should have: student_db_id, student_id, student_name, embeddings (list of np arrays)
        """
        self._known_embeddings.clear()
        for data in embeddings_data:
            self._known_embeddings[data['student_db_id']] = {
                'student_id': data['student_id'],
                'student_name': data['student_name'],
                'embeddings': data['embeddings']  # list of np.ndarray
            }
        logger.info(f"Loaded embeddings for {len(self._known_embeddings)} students")
    
    def add_embedding(self, student_db_id: int, student_id: str, student_name: str, 
                      embeddings: list[np.ndarray]):
        """Add or update embeddings for a student."""
        self._known_embeddings[student_db_id] = {
            'student_id': student_id,
            'student_name': student_name,
            'embeddings': embeddings
        }
    
    def remove_embedding(self, student_db_id: int):
        """Remove embeddings for a student."""
        self._known_embeddings.pop(student_db_id, None)
    
    def _compute_distance(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute distance between two embeddings."""
        if self.use_cosine:
            # Cosine distance = 1 - cosine_similarity
            dot = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            if norm1 == 0 or norm2 == 0:
                return 1.0
            similarity = dot / (norm1 * norm2)
            return 1.0 - similarity
        else:
            # Euclidean distance
            return float(np.linalg.norm(emb1 - emb2))
    
    def match_face(self, query_embedding: np.ndarray) -> MatchResult:
        """
        Match a query embedding against all known embeddings.
        Returns the best match if distance is below threshold.
        """
        if not self._known_embeddings:
            return MatchResult(matched=False, distance=float('inf'))
        
        best_distance = float('inf')
        best_match_id = None
        
        for student_db_id, data in self._known_embeddings.items():
            for known_emb in data['embeddings']:
                distance = self._compute_distance(query_embedding, known_emb)
                if distance < best_distance:
                    best_distance = distance
                    best_match_id = student_db_id
        
        if best_match_id is not None and best_distance <= self.threshold:
            data = self._known_embeddings[best_match_id]
            confidence = max(0.0, 1.0 - (best_distance / self.threshold))
            return MatchResult(
                matched=True,
                student_db_id=best_match_id,
                student_id=data['student_id'],
                student_name=data['student_name'],
                distance=round(best_distance, 4),
                confidence=round(confidence, 4)
            )
        
        return MatchResult(
            matched=False,
            distance=round(best_distance, 4),
            confidence=0.0
        )
    
    def match_faces(self, query_embeddings: list[np.ndarray]) -> list[MatchResult]:
        """Match multiple face embeddings."""
        return [self.match_face(emb) for emb in query_embeddings]
    
    @property
    def num_registered(self) -> int:
        return len(self._known_embeddings)
