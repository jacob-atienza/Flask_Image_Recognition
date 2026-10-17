"""Test cases for the model."""

from io import BytesIO
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image, UnidentifiedImageError

import model as model_module
from model import preprocess_img, predict_result  # Adjust based on your structure

# Basic Tests

def test_preprocess_img():
    """Test the preprocess_img function."""
    img_path = "test_images/2/Sign 2 (97).jpeg"
    processed_img = preprocess_img(img_path)

    # Check that the output shape is as expected
    assert processed_img.shape == (1, 224, 224, 3), \
        "Processed image shape should be (1, 224, 224, 3)"

    # Check that values are normalized (between 0 and 1)
    assert np.min(processed_img) >= 0 and np.max(processed_img) <= 1, \
        "Image pixel values should be normalized between 0 and 1"


def test_predict_result():
    """Test the predict_result function."""
    img_path = "test_images/4/Sign 4 (92).jpeg"  # Ensure the path is correct
    processed_img = preprocess_img(img_path)

    # Make a prediction
    prediction = predict_result(processed_img)

    # Print the prediction for debugging
    print(f"Prediction: {prediction} (Type: {type(prediction)})")

    # Check that the prediction is an integer (convert if necessary)
    assert isinstance(prediction, (int, np.integer)), "Prediction should be an integer class index"


# Advanced Tests

def test_invalid_image_path():
    """Test preprocess_img with an invalid image path."""
    with pytest.raises(FileNotFoundError):
        preprocess_img("invalid/path/to/image.jpeg")

@pytest.mark.parametrize("scores, expected", [
    ([0.8, 0.1, 0.1], 0),
    ([0.1, 0.2, 0.7], 2),
    ([0.5, 0.5, 0.0], 0),
])
def test_predict_result_selects_highest_score(monkeypatch, scores, expected):
    """Select the highest score, taking the first index when scores tie."""
    mock_model = Mock()
    mock_model.predict.return_value = np.array([scores])
    monkeypatch.setattr(model_module, "model", mock_model)
    image_batch = np.zeros((1, 224, 224, 3))

    assert predict_result(image_batch) == expected
    mock_model.predict.assert_called_once_with(image_batch)


@pytest.mark.parametrize("color", [(0, 0, 0), (255, 255, 255), (64, 128, 192)])
def test_preprocess_known_pixels(color):
    """Resize RGB uploads and preserve channel order while normalizing pixels."""
    image_data = BytesIO()
    Image.new("RGB", (40, 60), color=color).save(image_data, format="PNG")
    image_data.seek(0)

    processed = preprocess_img(image_data)

    assert processed.shape == (1, 224, 224, 3)
    expected = np.broadcast_to(np.array(color) / 255.0, processed.shape)
    np.testing.assert_allclose(processed, expected)


@pytest.mark.parametrize("contents", [b"", b"not an image"])
def test_preprocess_rejects_invalid_image(contents):
    """Reject empty uploads and bytes that do not represent an image."""
    with pytest.raises(UnidentifiedImageError):
        preprocess_img(BytesIO(contents))

def test_model_predictions_consistency():
    """Test that predictions for the same input are consistent."""
    img_path = "test_images/7/Sign 7 (54).jpeg"
    processed_img = preprocess_img(img_path)

    # Make multiple predictions
    predictions = [predict_result(processed_img) for _ in range(5)]

    # Check that all predictions are the same
    assert all(p == predictions[0] for p in predictions), \
        "Predictions for the same input should be consistent"
