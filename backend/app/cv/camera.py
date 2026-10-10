import cv2
import numpy as np
import base64
import logging

logger = logging.getLogger(__name__)

def decode_base64_image(base64_string: str) -> np.ndarray | None:
    """Decode a base64 encoded image string to a numpy array."""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        img_bytes = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        return None

def encode_image_base64(image: np.ndarray, format: str = '.jpg') -> str:
    """Encode a numpy image to base64 string."""
    _, buffer = cv2.imencode(format, image)
    return base64.b64encode(buffer).decode('utf-8')

def resize_for_processing(image: np.ndarray, max_width: int = 640) -> np.ndarray:
    """Resize image for faster processing while maintaining aspect ratio."""
    h, w = image.shape[:2]
    if w <= max_width:
        return image
    scale = max_width / w
    new_h = int(h * scale)
    return cv2.resize(image, (max_width, new_h), interpolation=cv2.INTER_AREA)

def draw_face_boxes(image: np.ndarray, faces: list, names: list[str] | None = None) -> np.ndarray:
    """Draw bounding boxes and names on detected faces."""
    output = image.copy()
    for i, face in enumerate(faces):
        x, y, w, h = face.bbox
        # Green for recognized, red for unknown
        name = names[i] if names and i < len(names) else "Unknown"
        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
        
        # Draw name label
        label_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(output, (x, y - label_size[1] - 10), 
                     (x + label_size[0], y), color, -1)
        cv2.putText(output, name, (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return output
