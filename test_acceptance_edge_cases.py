"""Verify image upload edge cases with valid images and meaningful results."""

from io import BytesIO
import re
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image

import app as app_module


def _image_data(image_format, size, color):
    """Create an RGB upload without optional metadata."""
    image_data = BytesIO()
    Image.new("RGB", size, color=color).save(
        image_data, format=image_format, compress_level=0
    )
    image_data.seek(0)
    return image_data


@pytest.mark.parametrize("image_format, size, headers", [
    pytest.param("PNG", (2048, 2048), {}, id="valid-image-over-10-MB"),
    pytest.param("PNG", (80, 60), {}, id="image-without-optional-metadata"),
    pytest.param("WEBP", (80, 60), {}, id="actual-webp-image"),
    pytest.param(
        "PNG", (80, 60), {"X-Unexpected-Header": "value"}, id="unexpected-header"
    ),
])
def test_valid_image_upload_edge_cases(client, image_format, size, headers):
    """Return a digit for valid large, metadata-free, WebP, and header cases."""
    image_data = _image_data(image_format, size, (64, 128, 192))
    if size == (2048, 2048):
        assert image_data.getbuffer().nbytes > 10 * 1024 * 1024

    response = client.post(
        "/prediction",
        data={"file": (image_data, f"image.{image_format.lower()}")},
        content_type="multipart/form-data",
        headers=headers,
    )

    assert response.status_code == 200
    assert b"File cannot be processed." not in response.data
    assert re.search(rb'<h2[^>]*>\s*[0-9]\s*</h2>', response.data)


def test_sequential_uploads_use_each_image(client, monkeypatch):
    """Preprocess each upload separately and display its own prediction."""
    predictor = Mock(side_effect=[2, 7])
    monkeypatch.setattr(app_module, "predict_result", predictor)

    for color, expected in [((0, 0, 0), 2), ((255, 255, 255), 7)]:
        response = client.post(
            "/prediction",
            data={"file": (_image_data("PNG", (80, 60), color), "image.png")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert re.search(rb'<h2[^>]*>\s*%d\s*</h2>' % expected, response.data)

    assert predictor.call_count == 2
    for call, expected_pixel in zip(predictor.call_args_list, [0.0, 1.0]):
        batch = call.args[0]
        assert batch.shape == (1, 224, 224, 3)
        np.testing.assert_allclose(batch, expected_pixel)
