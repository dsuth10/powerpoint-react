import pytest
from unittest.mock import patch, MagicMock
from app.services.pptx import build_pptx, PPTXBuilderError
from app.models.slides import SlidePlan, ImageMeta
from pathlib import Path
import os

def make_slide(title="T", body="B", image_url=None, notes=None):
    img = ImageMeta(url=image_url, alt="desc", provider="runware") if image_url else None
    return SlidePlan(title=title, body=body, image=img, notes=notes)

@patch("app.services.pptx.download_image")
def test_build_pptx_with_image_and_notes(mock_download):
    mock_download.side_effect = [b"img-bytes", None, b"img-bytes"]
    slides = [make_slide(image_url="http://img", notes="Speaker notes")] * 2
    out_path = build_pptx(slides, output_dir="/tmp")
    assert isinstance(out_path, Path)
    assert out_path.exists()
    os.remove(out_path)

@patch("app.services.pptx.download_image")
def test_build_pptx_image_download_fails(mock_download):
    mock_download.side_effect = [None, b"fallback-bytes"]
    slides = [make_slide(image_url="bad-url")]
    out_path = build_pptx(slides, output_dir="/tmp")
    assert out_path.exists()
    os.remove(out_path) 