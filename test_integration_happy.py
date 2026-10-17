"""Test cases for integration of the happy path scenarios."""

# test_integration_happy.py

from io import BytesIO
import re

def test_successful_prediction(client):
    """Test the successful image upload and prediction."""
    # Simulate a file upload to the correct prediction endpoint
    with open("test_images/0/Sign 0 (21).jpeg", "rb") as f:
        img_data = BytesIO(f.read())
    img_data.name = "test_image.jpg"

    # Simulate a file upload to the correct prediction endpoint
    response = client.post(
        "/prediction",  # Correct route for prediction
        data={"file": (img_data, img_data.name)},
        content_type="multipart/form-data"
    )

    # Assertions
    assert response.status_code == 200
    assert re.search(
    rb'<h2[^>]*>\s*[0-9]\s*</h2>',
    response.data,
)

def test_home_page(client):
    """Test the home page route."""
    response = client.get("/")
    assert response.status_code == 200
