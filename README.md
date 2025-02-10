# PDF to Markdown Converter

A high-performance PDF to Markdown converter that handles complex documents including images, diagrams, LaTeX equations, and tables. Powered by Google's Gemini Vision API for accurate document understanding.

## Features

- Fast conversion (< 5 seconds for 20-page documents)
- Preserves document structure and formatting
- Handles complex elements:
  - Images and diagrams
  - Mathematical equations
  - Tables
  - Nested lists
  - Text formatting (bold, italic, etc.)
- Maintains proper heading hierarchy
- Automatic image extraction and optimization
- Parallel processing for better performance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf2md-core.git
cd pdf2md-core
```

2. Install system dependencies:
```bash
# macOS
chmod +x install_dependencies.sh
./install_dependencies.sh
```

3. Set up environment:
```bash
# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Usage

Convert a PDF file to Markdown:
```bash
python src/cli.py input.pdf
```

Specify custom output path:
```bash
python src/cli.py input.pdf -o output.md
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest tests/
```

## Architecture

The converter uses a three-stage pipeline:

1. **Image Processing** (`ImageProcessor`)
   - Converts PDF pages to high-quality images
   - Extracts embedded images
   - Handles OCR when needed

2. **Content Analysis** (`GeminiProcessor`)
   - Uses Gemini Vision API for layout analysis
   - Detects document structure and elements
   - Processes mathematical equations

3. **Markdown Assembly** (`MarkdownAssembler`)
   - Converts processed elements to Markdown
   - Maintains proper document structure
   - Handles formatting and special elements

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini Vision API for document understanding
- PyMuPDF for PDF processing
- Tesseract OCR for text extraction
