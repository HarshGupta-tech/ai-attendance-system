import numpy as np
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetrics:
    """Face recognition evaluation metrics."""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    false_acceptance_rate: float = 0.0  # FAR
    false_rejection_rate: float = 0.0  # FRR
    avg_recognition_latency_ms: float = 0.0
    threshold_used: float = 0.0
    total_tests: int = 0
    true_positives: int = 0
    true_negatives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    status: str = "pending"  # pending, completed, error
    notes: str = ""

class ModelEvaluator:
    """
    Evaluates face recognition model performance.
    
    Tests recognition accuracy, precision, recall, F1-score,
    false acceptance rate (FAR), and false rejection rate (FRR)
    at various thresholds.
    """
    
    def __init__(self, matcher, encoder):
        self.matcher = matcher
        self.encoder = encoder
    
    def evaluate(self, test_data: list[dict], thresholds: list[float] | None = None) -> dict[float, EvaluationMetrics]:
        """
        Evaluate recognition performance.
        
        test_data: list of dicts with:
            - 'image': np.ndarray (face image)
            - 'expected_student_db_id': int | None (None for unknown faces)
            - 'label': str (description)
        
        Returns: dict mapping threshold -> EvaluationMetrics
        """
        if thresholds is None:
            thresholds = [0.4, 0.5, 0.6, 0.7, 0.8]
        
        results = {}
        
        for threshold in thresholds:
            self.matcher.threshold = threshold
            metrics = EvaluationMetrics(threshold_used=threshold)
            latencies = []
            
            for test in test_data:
                image = test['image']
                expected_id = test.get('expected_student_db_id')
                
                start = time.time()
                embedding = self.encoder.encode_face(image)
                if embedding is None:
                    if expected_id is not None:
                        metrics.false_negatives += 1  # Should have recognized
                    else:
                        metrics.true_negatives += 1  # Correctly rejected
                    continue
                
                match = self.matcher.match_face(embedding)
                latency = (time.time() - start) * 1000
                latencies.append(latency)
                
                if expected_id is not None:
                    # This is a known person
                    if match.matched and match.student_db_id == expected_id:
                        metrics.true_positives += 1
                    elif match.matched and match.student_db_id != expected_id:
                        metrics.false_positives += 1
                    else:
                        metrics.false_negatives += 1
                else:
                    # This is an unknown person
                    if match.matched:
                        metrics.false_positives += 1
                    else:
                        metrics.true_negatives += 1
            
            metrics.total_tests = len(test_data)
            
            tp = metrics.true_positives
            tn = metrics.true_negatives
            fp = metrics.false_positives
            fn = metrics.false_negatives
            
            # Calculate metrics
            total = tp + tn + fp + fn
            metrics.accuracy = (tp + tn) / total if total > 0 else 0.0
            metrics.precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            metrics.recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            
            if metrics.precision + metrics.recall > 0:
                metrics.f1_score = 2 * (metrics.precision * metrics.recall) / (metrics.precision + metrics.recall)
            
            # FAR = FP / (FP + TN)
            metrics.false_acceptance_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            # FRR = FN / (FN + TP)
            metrics.false_rejection_rate = fn / (fn + tp) if (fn + tp) > 0 else 0.0
            
            metrics.avg_recognition_latency_ms = float(np.mean(latencies)) if latencies else 0.0
            metrics.status = "completed"
            
            # Round all floats
            for field_name in ['accuracy', 'precision', 'recall', 'f1_score',
                             'false_acceptance_rate', 'false_rejection_rate',
                             'avg_recognition_latency_ms']:
                setattr(metrics, field_name, round(getattr(metrics, field_name), 4))
            
            results[threshold] = metrics
            logger.info(
                f"Threshold {threshold}: Acc={metrics.accuracy}, "
                f"P={metrics.precision}, R={metrics.recall}, F1={metrics.f1_score}, "
                f"FAR={metrics.false_acceptance_rate}, FRR={metrics.false_rejection_rate}"
            )
        
        return results
    
    def find_optimal_threshold(self, test_data: list[dict],
                                thresholds: list[float] | None = None) -> tuple[float, EvaluationMetrics]:
        """Find the threshold that maximizes F1-score."""
        if thresholds is None:
            thresholds = [round(t * 0.05, 2) for t in range(6, 18)]  # 0.3 to 0.85
        
        results = self.evaluate(test_data, thresholds)
        
        best_threshold = 0.6
        best_f1 = 0.0
        
        for threshold, metrics in results.items():
            if metrics.f1_score > best_f1:
                best_f1 = metrics.f1_score
                best_threshold = threshold
        
        return best_threshold, results[best_threshold]
