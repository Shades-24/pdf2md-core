import fitz  # PyMuPDF
from typing import Tuple, List, Dict, Optional
from pathlib import Path
import os
import tempfile

from .processor.image_processor import ImageProcessor
from .processor.latex_processor import LatexProcessor
from .processor.footnote_processor import FootnoteProcessor
from .processor.heading_processor import HeadingProcessor
from .processor.markdown_assembler import MarkdownAssembler

class PDFConverter:
    def __init__(self, 
                 image_processor: Optional[ImageProcessor] = None,
                 latex_processor: Optional[LatexProcessor] = None,
                 footnote_processor: Optional[FootnoteProcessor] = None,
                 heading_processor: Optional[HeadingProcessor] = None):
        """Initialize the PDF converter with optional processors."""
        self.image_processor = image_processor
        self.latex_processor = latex_processor or LatexProcessor()
        self.footnote_processor = footnote_processor or FootnoteProcessor()
        self.heading_processor = heading_processor or HeadingProcessor()
        self.markdown_assembler = MarkdownAssembler()
        
    def extract_page_content(self, page: fitz.Page, temp_dir: str) -> Tuple[str, List[Dict], Dict, List[Dict]]:
        """Extract text, images, and font info from a page."""
        text_blocks = []
        structured_blocks = []
        images = []
        font_info = {}
        
        # Get page dimensions for relative positioning
        page_width = page.rect.width
        page_height = page.rect.height
        
        # First pass: Extract text and build structured blocks
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # Text block
                block_text = []
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if text.strip():
                            position = len('\n'.join(text_blocks))
                            font_info[position] = (span["size"], span["flags"] & 2 != 0)  # size and bold flag
                            block_text.append(text)
                
                if block_text:
                    full_text = ' '.join(block_text)
                    text_blocks.append(full_text)
                    # Store structured block info
                    structured_blocks.append({
                        'text': full_text,
                        'x': block["bbox"][0] / page_width,  # Normalize coordinates
                        'y': block["bbox"][1] / page_height,
                        'width': (block["bbox"][2] - block["bbox"][0]) / page_width,
                        'height': (block["bbox"][3] - block["bbox"][1]) / page_height,
                        'position': len('\n'.join(text_blocks))  # Store position for image placement
                    })
        
        # Extract images using the image processor
        if self.image_processor:
            images = self.image_processor.extract_images(page, temp_dir)
            
            # Find nearest text position for each image
            for img in images:
                img_y = img['y']
                min_distance = float('inf')
                position = 0
                
                for block in structured_blocks:
                    block_y = block.get('y', 0)
                    distance = abs(img_y - block_y)
                    if distance < min_distance:
                        min_distance = distance
                        position = block.get('position', 0)
                
                img['position'] = position
                
        return '\n'.join(text_blocks), images, font_info, structured_blocks
        
    def convert(self, pdf_path: str) -> Tuple[str, List[Dict], str, List[Dict]]:
        """Convert PDF to markdown with images and table of contents."""
        self.doc = fitz.open(pdf_path)
        all_text = []
        all_images = []
        all_font_info = {}
        all_blocks = []
        current_position = 0
        
        # Create temporary directory for image processing
        temp_dir = tempfile.mkdtemp(prefix='pdf2md_')
        
        try:
            # Process each page
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                text, images, font_info, blocks = self.extract_page_content(page, temp_dir)
                
                # Update positions for font info
                offset_font_info = {
                    k + current_position: v for k, v in font_info.items()
                }
                all_font_info.update(offset_font_info)
                
                # Update positions for images and blocks
                for img in images:
                    img['position'] += current_position
                    img['y'] += page_num  # Adjust y-coordinate for page number
                all_images.extend(images)
                
                # Update blocks with page offset
                for block in blocks:
                    block['y'] += page_num  # Adjust y-coordinate for page number
                all_blocks.extend(blocks)
                
                all_text.append(text)
                current_position += len(text) + 1  # +1 for newline
                
            # Combine all text
            combined_text = '\n\n'.join(all_text)
            
            # Process with specialized processors
            # Handle LaTeX equations
            if self.latex_processor.detect_latex(combined_text):
                combined_text = self.latex_processor.convert_to_markdown(combined_text)
                
            # Process headings and generate TOC
            processed_text = self.heading_processor.convert_to_markdown(combined_text, all_font_info)
            headings = self.heading_processor.extract_headings(combined_text, all_font_info)
            toc = self.heading_processor.get_table_of_contents(headings)
            
            # Handle footnotes
            processed_text = self.footnote_processor.convert_to_markdown(processed_text)
            
            # Assemble final markdown with text blocks
            final_markdown = self.markdown_assembler.assemble(
                processed_text,
                all_images,
                toc=toc,
                text_blocks=all_blocks
            )
            
            return final_markdown, all_images, toc, all_blocks
            
        finally:
            self.doc.close()
            # Clean up temporary files
            if self.image_processor:
                self.image_processor.cleanup(temp_dir)
            
def convert_pdf_to_markdown(pdf_path: str,
                          image_processor: Optional[ImageProcessor] = None,
                          latex_processor: Optional[LatexProcessor] = None,
                          footnote_processor: Optional[FootnoteProcessor] = None,
                          heading_processor: Optional[HeadingProcessor] = None) -> Tuple[str, List[Dict], str, List[Dict]]:
    """Convenience function to convert a PDF file to markdown."""
    converter = PDFConverter(
        image_processor=image_processor,
        latex_processor=latex_processor,
        footnote_processor=footnote_processor,
        heading_processor=heading_processor
    )
    return converter.convert(pdf_path)
