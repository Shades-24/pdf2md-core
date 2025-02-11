import argparse
import sys
from pathlib import Path
from typing import Optional
import os

from .processor.image_processor import ImageProcessor
from .processor.latex_processor import LatexProcessor
from .processor.footnote_processor import FootnoteProcessor
from .processor.heading_processor import HeadingProcessor
from .converter import convert_pdf_to_markdown

def setup_argparser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert PDF files to Markdown with advanced features"
    )
    
    parser.add_argument(
        "input",
        help="Input PDF file or directory",
        nargs='?'  # Make input optional
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output directory for markdown files (default: same as input)",
        type=str
    )
    
    parser.add_argument(
        "--image-quality",
        help="Image quality (1-100, default: 75)",
        type=int,
        default=75
    )
    
    parser.add_argument(
        "--max-image-size",
        help="Maximum image dimension in pixels (default: 800)",
        type=int,
        default=800
    )
    
    parser.add_argument(
        "--disable-latex",
        help="Disable LaTeX equation processing",
        action="store_true"
    )
    
    parser.add_argument(
        "--disable-footnotes",
        help="Disable footnote processing",
        action="store_true"
    )
    
    parser.add_argument(
        "--disable-toc",
        help="Disable table of contents generation",
        action="store_true"
    )
    
    parser.add_argument(
        "--web",
        help="Start web interface",
        action="store_true"
    )
    
    parser.add_argument(
        "--port",
        help="Port for web interface (default: 8000)",
        type=int,
        default=8000
    )
    
    return parser

def process_file(input_path: Path, output_dir: Path, args: argparse.Namespace) -> Optional[str]:
    """Process a single PDF file."""
    try:
        # Initialize processors based on arguments
        image_processor = ImageProcessor()
        image_processor.max_dimension = args.max_image_size
        
        latex_processor = None if args.disable_latex else LatexProcessor()
        footnote_processor = None if args.disable_footnotes else FootnoteProcessor()
        heading_processor = None if args.disable_toc else HeadingProcessor()
        
        # Convert PDF to markdown
        markdown, images, toc = convert_pdf_to_markdown(
            str(input_path),
            image_processor=image_processor,
            latex_processor=latex_processor,
            footnote_processor=footnote_processor,
            heading_processor=heading_processor
        )
        
        # Create output filename
        output_file = output_dir / f"{input_path.stem}.md"
        
        # Save markdown
        output_file.write_text(markdown, encoding='utf-8')
        
        return str(output_file)
        
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}", file=sys.stderr)
        return None

def process_directory(input_dir: Path, output_dir: Path, args: argparse.Namespace) -> list:
    """Process all PDF files in a directory."""
    results = []
    for pdf_file in input_dir.glob("**/*.pdf"):
        if result := process_file(pdf_file, output_dir, args):
            results.append(result)
    return results

def main():
    """Main entry point."""
    parser = setup_argparser()
    args = parser.parse_args()
    
    # Handle web interface
    if args.web:
        from .web.app import run_server
        run_server(port=args.port)
        return
        
    # Require input path for CLI mode
    if not args.input:
        parser.error("Input path is required when not using --web")
        
    # Process input path
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)
        
    # Determine output directory
    output_dir = Path(args.output) if args.output else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process files
    if input_path.is_file():
        if result := process_file(input_path, output_dir, args):
            print(f"Successfully converted: {result}")
    else:
        results = process_directory(input_path, output_dir, args)
        if results:
            print(f"Successfully converted {len(results)} files:")
            for result in results:
                print(f"  {result}")
        else:
            print("No PDF files were converted")

if __name__ == "__main__":
    main()
