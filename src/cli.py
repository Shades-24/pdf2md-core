#!/usr/bin/env python3
import argparse
import os
import sys
from converter import PDFConverter

def convert_pdf(input_path: str, output_path: str = None) -> None:
    """Convert PDF to Markdown maintaining exact content order."""
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)
    
    if not output_path:
        output_path = os.path.splitext(input_path)[0] + '.md'
    
    try:
        # Initialize converter with output directory from output path
        output_dir = os.path.dirname(output_path) or "."
        
        converter = PDFConverter(output_dir=output_dir)
        result_path = converter.convert_pdf(input_path)
        
        # Rename if needed to match requested output path
        if result_path != output_path:
            os.rename(result_path, output_path)
            print(f"\nOutput saved to: {output_path}")
            
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF documents to Markdown format with embedded base64 images"
    )
    parser.add_argument(
        'input',
        help='Path to input PDF file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to output markdown file (default: input_name.md)',
        default=None
    )
    
    args = parser.parse_args()
    convert_pdf(args.input, args.output)

if __name__ == '__main__':
    main()
