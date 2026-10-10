from sqlalchemy.orm import Session
from app.models import FaceEmbedding, Student
import json
import base64
import numpy as np

class FaceService:
    def __init__(self, db: Session):
        self.db = db
        from app.ml.recognition_pipeline import get_pipeline
        self.pipeline = get_pipeline()
    
    def register_face(self, student_id: int, base64_images: list[str]) -> dict:
        """
        Register a student's face from multiple base64 images.
        1. Decode images
        2. Run through pipeline.register_face()
        3. Store embeddings in database
        4. Update matcher cache
        """
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Decode base64 images
        from app.cv.camera import decode_base64_image
        images = []
        for b64 in base64_images:
            img = decode_base64_image(b64)
            if img is not None:
                images.append(img)
                
        if not images:
            return {"success": False, "message": "Failed to decode any images"}
            
        result = self.pipeline.register_face(images)
        if not result.get("success"):
            return result
            
        embeddings = result.get("encodings", [])
            
        # Clear old embeddings
        self.db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student_id).delete()
        
        # Save new embeddings (as a list of embeddings in a single row)
        emb_list = [emb.tolist() for emb in embeddings]
        fe = FaceEmbedding(
            student_id=student_id,
            embedding_data=json.dumps(emb_list),
            num_samples=len(embeddings),
            quality_score=result.get("quality_score", 0.0)
        )
        self.db.add(fe)
        self.db.commit()
        
        self.load_all_embeddings()
        
        # Remove numpy arrays from result before returning to prevent JSON serialization errors
        if "encodings" in result:
            del result["encodings"]
            
        return result
    
    def get_registration_status(self, student_id: int) -> dict:
        """Check if a student has registered face data."""
        count = self.db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student_id).count()
        return {
            "student_id": student_id,
            "is_registered": count > 0,
            "samples_count": count
        }
    
    def delete_face_data(self, student_id: int) -> bool:
        """Delete face embeddings for a student (privacy feature)."""
        deleted = self.db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student_id).delete()
        self.db.commit()
        if deleted > 0:
            self.pipeline.matcher.remove_embedding(student_id)
        return deleted > 0
    
    def load_all_embeddings(self):
        """Load all face embeddings into the matcher cache."""
        embeddings = self.db.query(FaceEmbedding, Student).join(Student).all()
        self.pipeline.matcher._known_embeddings.clear()
        
        for fe, student in embeddings:
            try:
                data = json.loads(fe.embedding_data)
                # If it's a list of lists, convert to list of np.ndarrays
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    emb_arrays = [np.array(e, dtype=np.float32) for e in data]
                else:
                    # Fallback for old single-embedding format
                    emb_arrays = [np.array(data, dtype=np.float32)]
                    
                self.pipeline.matcher.add_embedding(
                    student_db_id=student.id, 
                    student_id=student.student_id, 
                    student_name=student.full_name, 
                    embeddings=emb_arrays
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to load embedding for student {student.id}: {e}")

    def verify_face(self, student_id: int, base64_image: str) -> dict:
        """
        Verify that a face image matches a specific student.
        Returns {'verified': True/False, 'confidence': float, 'message': str}
        """
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {"verified": False, "confidence": 0.0, "message": "Student not found"}

        # Check if student has registered face
        count = self.db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student_id).count()
        if count == 0:
            return {"verified": False, "confidence": 0.0, "message": "Face not registered. Please register your face first."}

        # Process the image through the pipeline
        result = self.pipeline.process_base64_frame(base64_image)

        if not result.faces:
            return {"verified": False, "confidence": 0.0, "message": "No face detected in image. Please try again."}

        # Check if any detected face matches this student
        for face in result.faces:
            if face.match.matched and face.match.student_db_id == student_id:
                return {
                    "verified": True,
                    "confidence": face.match.confidence,
                    "message": f"Face verified for {student.full_name}"
                }

        return {"verified": False, "confidence": 0.0, "message": "Face does not match. Proxy attendance is not allowed."}
