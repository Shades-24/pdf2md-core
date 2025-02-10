#!/usr/bin/env python3
import asyncio
import argparse
import os
import sys
from processor.image_processor import ImageProcessor
from processor.gemini_integration import GeminiProcessor
from processor.markdown_assembler import MarkdownAssembler
from dotenv import load_dotenv
import time

async def convert_pdf(input_path: str, output_path: str = None) -> None:
    """Convert PDF to Markdown with progress tracking."""
    start_time = time.time()
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)
    
    if not output_path:
        output_path = os.path.splitext(input_path)[0] + '.md'
    
    try:
        # Initialize processors
        image_proc = ImageProcessor()
        gemini_proc = GeminiProcessor()
        md_assembler = MarkdownAssembler()
        
        # Convert PDF pages to images
        print("Converting PDF pages to images...")
        image_paths = await image_proc.pdf_to_images(input_path)
        
        # Process images with Gemini
        print(f"Processing {len(image_paths)} pages with Gemini Vision API...")
        processed_pages = await gemini_proc.batch_process(image_paths)
        
        # Assemble markdown
        print("Assembling markdown document...")
        markdown_content = md_assembler.assemble_document(processed_pages)
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Cleanup temporary files
        print("Cleaning up temporary files...")
        if image_paths:
            image_proc.cleanup(os.path.dirname(image_paths[0]))
        
        elapsed_time = time.time() - start_time
        print(f"\nConversion completed in {elapsed_time:.2f} seconds")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF documents to Markdown format"
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
    
    # Load environment variables
    load_dotenv()
    
    # Verify API key
    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY not found in environment")
        print("Please set it in .env file or environment variables")
        sys.exit(1)
    
    # Run conversion
    asyncio.run(convert_pdf(args.input, args.output))

if __name__ == '__main__':
    main()
