import uuid
from pathlib import Path
from typing import List, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
import requests
from app.models.slides import SlidePlan

BRANDED_PLACEHOLDER = "https://placehold.co/600x400?text=Image+Unavailable"

class PPTXBuilderError(Exception):
    """Custom exception for PPTX builder errors."""
    pass

def download_image(url: str) -> Optional[bytes]:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None

def build_pptx(slides: List[SlidePlan], output_dir: str = "/tmp") -> Path:
    """
    Builds a PPTX file from a list of SlidePlan objects.
    Embeds images and speaker notes. If image download fails, inserts a branded placeholder.
    Returns the path to the generated PPTX file.
    """
    prs = Presentation()
    for slide_plan in slides:
        slide_layout = prs.slide_layouts[1]  # Title and Content
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = slide_plan.title
        body_shape = slide.shapes.placeholders[1]
        body_shape.text = slide_plan.body
        if slide_plan.image:
            img_bytes = download_image(slide_plan.image.url)
            if not img_bytes:
                img_bytes = download_image(BRANDED_PLACEHOLDER)
            if img_bytes:
                img_path = f"/tmp/{uuid.uuid4()}.img"
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
                slide.shapes.add_picture(img_path, Inches(1), Inches(2), width=Inches(4), height=Inches(3))
        if slide_plan.notes:
            slide.notes_slide.notes_text_frame.text = slide_plan.notes
    out_path = Path(output_dir) / f"{uuid.uuid4()}.pptx"
    prs.save(str(out_path))
    return out_path 