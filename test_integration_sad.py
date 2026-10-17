"""Test cases for integration of the sad path scenarios."""

# test_integration_sad.py

def test_missing_file(client):
    """Test the prediction route with a missing file."""
    response = client.post("/prediction", data={}, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"File cannot be processed." in response.data  # Check if the error message is displayed

def test_invalid_file_type(client):
    """Test the prediction route with an invalid file type."""
    # Simulate a POST request with an invalid file type (e.g., a text file)
    response = client.post(
        "/prediction",
        data={"file": ("invalid_file.txt", b"Invalid content")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert b"File cannot be processed." in response.data  # Check if the error message is displayed

def test_empty_file(client):
    """Test the prediction route with an empty file."""
    # Simulate a POST request with an empty file
    response = client.post(
        "/prediction",
        data={"file": ("empty_file.jpg", b"")},
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert b"File cannot be processed." in response.data  # Check if the error message is displayed
