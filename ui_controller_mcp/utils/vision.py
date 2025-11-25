import cv2
import numpy as np
import base64
from pathlib import Path
from typing import List, Dict, Any, Tuple

class VisionEngine:
    """
    Handles computer vision tasks using OpenCV.
    """
    
    def __init__(self):
        pass

    def find_template(
        self, 
        screenshot_b64: str, 
        template_path: str, 
        confidence: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find occurrences of a template image within the screenshot.
        
        Args:
            screenshot_b64: Base64 encoded screenshot data
            template_path: Path to the template image file
            confidence: Match threshold (0.0 to 1.0)
            
        Returns:
            List of matches, each containing:
            - center_x, center_y: Coordinates of the center
            - x, y, w, h: Bounding box
            - confidence: The matching score
        """
        # Decode screenshot
        try:
            img_data = base64.b64decode(screenshot_b64)
            nparr = np.frombuffer(img_data, np.uint8)
            screenshot = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if screenshot is None:
                raise ValueError("Failed to decode screenshot")
        except Exception as e:
            raise ValueError(f"Invalid screenshot data: {e}")

        # Load template
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"Failed to load template from {template_path}")

        # Get dimensions
        h, w = template.shape[:2]
        
        # Match template
        # TM_CCOEFF_NORMED is good for general purpose matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        
        # Find locations above confidence
        locations = np.where(result >= confidence)
        locations = list(zip(*locations[::-1]))  # Convert to (x, y) tuples
        
        matches = []
        # Non-maximum suppression (simple version) to avoid duplicate matches for same object
        # We'll just group matches that are very close
        processed_points = []
        
        for loc in locations:
            x, y = loc
            # Check if this point is close to an already processed point
            is_duplicate = False
            for px, py in processed_points:
                if abs(x - px) < w/2 and abs(y - py) < h/2:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                score = float(result[y, x])
                matches.append({
                    "center_x": int(x + w/2),
                    "center_y": int(y + h/2),
                    "x": int(x),
                    "y": int(y),
                    "w": int(w),
                    "h": int(h),
                    "confidence": score
                })
                processed_points.append((x, y))
                
        # Sort by confidence descending
        matches.sort(key=lambda m: m["confidence"], reverse=True)
        
        return matches
