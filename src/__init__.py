"""PDF to Markdown converter package."""

from .converter import convert_pdf_to_markdown
from .processor.image_processor import ImageProcessor
from .processor.latex_processor import LatexProcessor
from .processor.footnote_processor import FootnoteProcessor
from .processor.heading_processor import HeadingProcessor

__version__ = "1.0.0"

__all__ = [
    "convert_pdf_to_markdown",
    "ImageProcessor",
    "LatexProcessor",
    "FootnoteProcessor",
    "HeadingProcessor"
]
