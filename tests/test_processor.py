import pytest
import os
import tempfile
from src.processor.image_processor import ImageProcessor
from src.processor.gemini_integration import GeminiProcessor
from src.processor.markdown_assembler import MarkdownAssembler, Element, ElementType

@pytest.fixture
def image_processor():
    return ImageProcessor(dpi=150)  # Lower DPI for faster tests

@pytest.fixture
def gemini_processor():
    return GeminiProcessor()

@pytest.fixture
def markdown_assembler():
    return MarkdownAssembler()

@pytest.fixture
def sample_pdf():
    # Create a temporary PDF file for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # TODO: Create minimal test PDF
        return f.name

@pytest.mark.asyncio
async def test_pdf_to_images(image_processor, sample_pdf):
    """Test PDF to image conversion."""
    try:
        image_paths = await image_processor.pdf_to_images(sample_pdf)
        assert len(image_paths) > 0
        assert all(os.path.exists(path) for path in image_paths)
        assert all(path.endswith('.png') for path in image_paths)
    finally:
        # Cleanup
        if image_paths:
            image_processor.cleanup(os.path.dirname(image_paths[0]))

@pytest.mark.asyncio
async def test_gemini_processing(gemini_processor):
    """Test Gemini Vision API processing."""
    test_image = "tests/sample_pdfs/test_page.png"
    if not os.path.exists(test_image):
        pytest.skip("Test image not found")
    
    result = await gemini_processor.process_page(test_image)
    assert isinstance(result, dict)
    assert 'markdown' in result
    assert 'elements' in result

def test_markdown_assembly(markdown_assembler):
    """Test markdown assembly from processed elements."""
    test_pages = [
        {
            'elements': [
                {
                    'type': 'heading',
                    'content': 'Test Document',
                    'position': {'x': 0, 'y': 0},
                    'metadata': {'level': 1}
                },
                {
                    'type': 'text',
                    'content': 'This is a test paragraph.',
                    'position': {'x': 0, 'y': 50}
                },
                {
                    'type': 'list',
                    'content': 'First item',
                    'position': {'x': 20, 'y': 100},
                    'metadata': {'level': 0, 'ordered': True}
                }
            ]
        }
    ]
    
    result = markdown_assembler.assemble_document(test_pages)
    assert '# Test Document' in result
    assert 'This is a test paragraph.' in result
    assert '1. First item' in result

def test_element_processing(markdown_assembler):
    """Test individual element processing."""
    # Test heading
    heading = Element(
        type=ElementType.HEADING,
        content='Test Heading',
        position={'x': 0, 'y': 0},
        metadata={'level': 2}
    )
    assert markdown_assembler._process_element(heading) == '## Test Heading'
    
    # Test text with formatting
    text = Element(
        type=ElementType.TEXT,
        content='This is **bold** and *italic* text',
        position={'x': 0, 'y': 0}
    )
    processed_text = markdown_assembler._process_element(text)
    assert '**bold**' in processed_text
    assert '*italic*' in processed_text
    
    # Test equation
    equation = Element(
        type=ElementType.EQUATION,
        content='E = mc^2',
        position={'x': 0, 'y': 0},
        metadata={'inline': True}
    )
    assert markdown_assembler._process_element(equation) == '$E = mc^2$'

def test_table_processing(markdown_assembler):
    """Test table element processing."""
    table = Element(
        type=ElementType.TABLE,
        content=[
            ['Header 1', 'Header 2'],
            ['Cell 1', 'Cell 2'],
            ['Cell 3', 'Cell 4']
        ],
        position={'x': 0, 'y': 0}
    )
    
    result = markdown_assembler._process_element(table)
    assert '| Header 1 | Header 2 |' in result
    assert '| --- | --- |' in result
    assert '| Cell 1 | Cell 2 |' in result

def test_nested_list_processing(markdown_assembler):
    """Test nested list processing."""
    elements = [
        Element(
            type=ElementType.LIST,
            content='First level',
            position={'x': 0, 'y': 0},
            metadata={'level': 0, 'ordered': False}
        ),
        Element(
            type=ElementType.LIST,
            content='Second level',
            position={'x': 20, 'y': 20},
            metadata={'level': 1, 'ordered': False}
        )
    ]
    
    results = [markdown_assembler._process_element(e) for e in elements]
    assert results[0] == '- First level'
    assert results[1] == '  - Second level'

if __name__ == '__main__':
    pytest.main([__file__])
