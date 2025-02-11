import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Create pytest fixtures here if needed
import pytest

@pytest.fixture
def test_pdf_path():
    """Get path to test PDF file."""
    return str(Path(__file__).parent / "sample_pdfs" / "test.pdf")
