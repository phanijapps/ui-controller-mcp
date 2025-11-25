import pytest
import numpy as np
import base64
from unittest.mock import patch, MagicMock
from ui_controller_mcp.utils.vision import VisionEngine

@pytest.fixture
def mock_cv2():
    with patch("ui_controller_mcp.utils.vision.cv2") as mock:
        yield mock

def test_find_template(mock_cv2):
    engine = VisionEngine()
    
    # Mock screenshot decoding
    mock_cv2.imdecode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Mock template loading
    mock_template = np.zeros((10, 10, 3), dtype=np.uint8)
    mock_cv2.imread.return_value = mock_template
    
    # Mock matchTemplate result
    # Create a result map where one point (50, 50) has high correlation
    mock_result = np.zeros((91, 91), dtype=np.float32)
    mock_result[50, 50] = 0.95
    mock_cv2.matchTemplate.return_value = mock_result
    mock_cv2.TM_CCOEFF_NORMED = 5
    
    # Create dummy base64 image (valid padding)
    dummy_b64 = base64.b64encode(b"fake_image_data").decode()
    
    matches = engine.find_template(dummy_b64, "template.png", confidence=0.8)
    
    assert len(matches) == 1
    match = matches[0]
    assert match["x"] == 50
    assert match["y"] == 50
    assert match["w"] == 10
    assert match["h"] == 10
    assert match["center_x"] == 55
    assert match["center_y"] == 55
    assert match["confidence"] == pytest.approx(0.95)

def test_find_template_no_match(mock_cv2):
    engine = VisionEngine()
    
    mock_cv2.imdecode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_cv2.imread.return_value = np.zeros((10, 10, 3), dtype=np.uint8)
    
    # Result with no high confidence matches
    mock_result = np.zeros((91, 91), dtype=np.float32)
    mock_cv2.matchTemplate.return_value = mock_result
    
    # Use valid base64
    dummy_b64 = base64.b64encode(b"fake_image_data").decode()
    matches = engine.find_template(dummy_b64, "template.png", confidence=0.8)
    assert len(matches) == 0
