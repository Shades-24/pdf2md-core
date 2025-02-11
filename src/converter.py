import fitz  # PyMuPDF
from typing import Tuple, List, Dict, Optional
from pathlib import Path
import os

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
        
    def extract_page_content(self, page: fitz.Page) -> Tuple[str, List[Dict], Dict]:
        """Extract text, images, and font info from a page."""
        text_blocks = []
        images = []
        font_info = {}
        
        # Extract text blocks with position and font info
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if text.strip():
                            position = len('\n'.join(text_blocks))
                            font_info[position] = (span["size"], span["flags"] & 2 != 0)  # size and bold flag
                            text_blocks.append(text)
            elif block["type"] == 1 and self.image_processor:  # Image block
                try:
                    image = page.get_images(full=True)[0]  # Get image data
                    xref = image[0]
                    base_image = self.doc.extract_image(xref)
                    image_data = base_image["image"]
                    
                    # Process image
                    image_b64 = self.image_processor.image_to_base64(image_data)
                    images.append({
                        'data': image_b64,
                        'rect': block["bbox"],
                        'position': len('\n'.join(text_blocks))
                    })
                except Exception as e:
                    print(f"Warning: Failed to process image: {e}")
                    continue
                    
        return '\n'.join(text_blocks), images, font_info
        
    def convert(self, pdf_path: str) -> Tuple[str, List[Dict], str]:
        """Convert PDF to markdown with images and table of contents."""
        self.doc = fitz.open(pdf_path)
        all_text = []
        all_images = []
        all_font_info = {}
        current_position = 0
        
        try:
            # Process each page
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                text, images, font_info = self.extract_page_content(page)
                
                # Update positions for font info
                offset_font_info = {
                    k + current_position: v for k, v in font_info.items()
                }
                all_font_info.update(offset_font_info)
                
                # Update positions for images
                for img in images:
                    img['position'] += current_position
                all_images.extend(images)
                    
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
            
            # Assemble final markdown
            final_markdown = self.markdown_assembler.assemble(
                processed_text,
                all_images,
                toc=toc
            )
            
            return final_markdown, all_images, toc
            
        finally:
            self.doc.close()
            
def convert_pdf_to_markdown(pdf_path: str,
                          image_processor: Optional[ImageProcessor] = None,
                          latex_processor: Optional[LatexProcessor] = None,
                          footnote_processor: Optional[FootnoteProcessor] = None,
                          heading_processor: Optional[HeadingProcessor] = None) -> Tuple[str, List[Dict], str]:
    """Convenience function to convert a PDF file to markdown."""
    converter = PDFConverter(
        image_processor=image_processor,
        latex_processor=latex_processor,
        footnote_processor=footnote_processor,
        heading_processor=heading_processor
    )
    return converter.convert(pdf_path)
