import pytest
from pathlib import Path
import os

from src.processor.image_processor import ImageProcessor
from src.processor.latex_processor import LatexProcessor
from src.processor.footnote_processor import FootnoteProcessor
from src.processor.heading_processor import HeadingProcessor
from src.converter import convert_pdf_to_markdown

@pytest.fixture
def test_pdf_path():
    """Get path to test PDF file."""
    return str(Path(__file__).parent / "sample_pdfs" / "test.pdf")

def test_image_processor():
    """Test image processor functionality."""
    processor = ImageProcessor()
    assert processor.max_dimension == 800
    assert hasattr(processor, 'image_to_base64')

def test_latex_processor():
    """Test LaTeX processor functionality."""
    processor = LatexProcessor()
    
    # Test LaTeX detection
    text_with_latex = r"This is an equation: \begin{equation} E = mc^2 \end{equation}"
    text_without_latex = "This is regular text"
    
    assert processor.detect_latex(text_with_latex)
    assert not processor.detect_latex(text_without_latex)
    
    # Test LaTeX conversion
    converted = processor.convert_to_markdown(text_with_latex)
    assert "$$" in converted
    assert "E = mc^2" in converted

def test_footnote_processor():
    """Test footnote processor functionality."""
    processor = FootnoteProcessor()
    
    text_with_footnote = "Here is some text[1] with a footnote.\n\n1. This is the footnote content"
    converted = processor.convert_to_markdown(text_with_footnote)
    
    assert "[^1]" in converted
    assert "[^1]:" in converted

def test_heading_processor():
    """Test heading processor functionality."""
    processor = HeadingProcessor()
    
    text_with_headings = """# Main Title
    ## Section 1
    Some content
    ## Section 2
    More content"""
    
    # Test heading detection
    headings = processor.extract_headings(text_with_headings)
    assert len(headings) == 3
    assert headings[0].level == 1
    assert headings[1].level == 2
    
    # Test TOC generation
    toc = processor.get_table_of_contents(headings)
    assert "Table of Contents" in toc
    assert "Main Title" in toc
    assert "Section 1" in toc

def test_full_conversion(test_pdf_path):
    """Test full PDF to markdown conversion."""
    # Initialize processors
    image_processor = ImageProcessor()
    latex_processor = LatexProcessor()
    footnote_processor = FootnoteProcessor()
    heading_processor = HeadingProcessor()
    
    # Convert PDF
    markdown, images, toc = convert_pdf_to_markdown(
        test_pdf_path,
        image_processor=image_processor,
        latex_processor=latex_processor,
        footnote_processor=footnote_processor,
        heading_processor=heading_processor
    )
    
    # Basic validation
    assert markdown, "Markdown output should not be empty"
    assert isinstance(markdown, str), "Markdown should be a string"
    assert isinstance(images, list), "Images should be a list"
    assert isinstance(toc, str), "TOC should be a string"

def test_image_quality():
    """Test image quality settings."""
    processor = ImageProcessor()
    
    # Test different quality settings
    processor.quality_settings['photo']['quality'] = 30
    processor.quality_settings['diagram']['quality'] = 50
    processor.quality_settings['icon']['quality'] = 60
    
    assert processor.quality_settings['photo']['quality'] == 30
    assert processor.quality_settings['diagram']['quality'] == 50
    assert processor.quality_settings['icon']['quality'] == 60

def test_latex_patterns():
    """Test LaTeX pattern recognition."""
    processor = LatexProcessor()
    
    # Test various LaTeX patterns
    patterns = [
        (r"\begin{equation} x = y \end{equation}", True),
        (r"$E = mc^2$", True),
        (r"\begin{align*} a &= b \\ c &= d \end{align*}", True),
        ("Regular text", False),
        ("$", False),
        (r"\begin{equation}", False)
    ]
    
    for text, should_detect in patterns:
        assert processor.detect_latex(text) == should_detect

def test_footnote_patterns():
    """Test footnote pattern recognition."""
    processor = FootnoteProcessor()
    
    # Test various footnote patterns
    text = """Here is text with a numbered footnote[1] and a symbol footnote[*].

1. First footnote content
* Second footnote content"""
    
    footnotes = processor.extract_footnotes(text)
    assert len(footnotes) == 2
    assert footnotes[0].id == "1"
    assert footnotes[1].id == "*"

def test_heading_levels():
    """Test heading level detection."""
    processor = HeadingProcessor()
    
    # Test heading level detection with font information
    text = "Test Heading"
    font_info = {0: (20.0, True)}  # Large, bold font
    
    level = processor.detect_heading_level(text, font_size=20.0, is_bold=True)
    assert level == 1  # Should be h1 based on font size

    # Test with different patterns
    assert processor.detect_heading_level("# Heading") == 1
    assert processor.detect_heading_level("1.2.3 Heading") == 3
    assert processor.detect_heading_level("ALL CAPS HEADING") == 2
