# PDF2MD Core

A Python-based tool for converting PDF documents to Markdown format, with special emphasis on preserving document structure, handling images intelligently, and supporting advanced features like LaTeX equations and footnotes.

## Features

- Smart image processing with type detection and optimization
- LaTeX equation support
- Footnote handling and reference linking
- Heading structure preservation
- Table of contents generation
- Web interface with real-time preview
- CLI for batch processing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf2md-core.git
cd pdf2md-core
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

### Web Interface

Start the web interface:
```bash
pdf2md --web
```
Then open http://localhost:8000 in your browser.

### CLI

Convert a single file:
```bash
pdf2md input.pdf -o output_dir
```

Convert a directory:
```bash
pdf2md input_directory -o output_dir
```

### Options

- `--output_dir PATH`: Directory where output files will be saved
- `--image-quality`: Image quality (1-100, default: 75)
- `--max-image-size`: Maximum image dimension in pixels (default: 800)
- `--disable-latex`: Disable LaTeX equation processing
- `--disable-footnotes`: Disable footnote processing
- `--disable-toc`: Disable table of contents generation
- `--port PORT`: Port for web interface (default: 8000)

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest tests/
```

## Project Structure

```
pdf2md-core/
├── src/
│   ├── processor/
│   │   ├── image_processor.py
│   │   ├── latex_processor.py
│   │   ├── footnote_processor.py
│   │   ├── heading_processor.py
│   │   └── markdown_assembler.py
│   ├── web/
│   │   ├── app.py
│   │   ├── templates/
│   │   └── static/
│   ├── cli.py
│   └── converter.py
├── tests/
│   └── sample_pdfs/
└── requirements.txt
```

## Features in Detail

### Image Processing
- Smart type detection (diagrams, photos, icons)
- Context-aware quality settings
- WebP compression with type-specific optimization
- Position-aware placement

### Document Structure
- Font size-based heading detection
- Pattern-based heading recognition
- Proper heading hierarchy
- Footnote reference linking
- LaTeX equation preservation

### Web Interface
- Modern, responsive design
- Real-time preview
- Error handling and validation
- Progress indication
- Download and copy options

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
