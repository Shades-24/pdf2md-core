import os
import io
import fitz
from typing import List, Dict, Any
from processor.image_processor import ImageProcessor
from processor.markdown_assembler import MarkdownAssembler

class PDFConverter:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.image_processor = ImageProcessor()
        self.markdown_assembler = MarkdownAssembler()
        os.makedirs(output_dir, exist_ok=True)
        
    def convert_pdf(self, pdf_path: str) -> str:
        """Convert PDF to markdown maintaining exact content order."""
        try:
            doc = fitz.open(pdf_path)
            markdown_content = []
            
            print("\nConverting PDF to Markdown...")
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                # Process each page
                page = doc[page_num]
                page_content = []
                
                # Get text blocks with positions
                text_dict = page.get_text("dict")
                
                # Get page dimensions
                page_height = page.rect.height
                
                # Extract text blocks and their positions
                text_blocks = []
                if "blocks" in text_dict:
                    for block in text_dict["blocks"]:
                        if block.get("type") == 0:  # Text block
                            bbox = block.get("bbox", [0, 0, 0, 0])
                            text = ""
                            for line in block.get("lines", []):
                                for span in line.get("spans", []):
                                    if span.get("text", "").strip():
                                        text += span["text"] + " "
                            if text.strip():
                                text_blocks.append({
                                    "text": text.strip(),
                                    "y": bbox[1],
                                    "height": bbox[3] - bbox[1]
                                })
                
                # Sort text blocks by vertical position
                text_blocks.sort(key=lambda x: x["y"])
                
                # Find gaps between text blocks
                gaps = []
                for i in range(len(text_blocks) - 1):
                    current_block_end = text_blocks[i]["y"] + text_blocks[i]["height"]
                    next_block_start = text_blocks[i + 1]["y"]
                    gap_size = next_block_start - current_block_end
                    if gap_size > 50:  # Significant gap that might indicate an image
                        gaps.append({
                            "y": current_block_end,
                            "size": gap_size
                        })
                
                # Get images
                images = page.get_images(full=True)
                print(f"\nPage {page_num + 1} analysis:")
                print(f"Found {len(text_blocks)} text blocks and {len(images)} images")
                print(f"Detected {len(gaps)} significant gaps in text")
                
                # Convert images to base64
                image_data = []
                for img_info in images:
                    try:
                        xref = img_info[0]
                        base_image = page.parent.extract_image(xref)
                        if base_image and base_image["image"]:
                            data_url = self.image_processor.image_to_base64(base_image["image"])
                            image_data.append(data_url)
                    except Exception as e:
                        print(f"\nWarning: Failed to process image: {str(e)}")
                
                # Build content by inserting images into gaps
                image_index = 0
                for i, block in enumerate(text_blocks):
                    # Add text block
                    formatted_text = self.markdown_assembler.format_text(block["text"])
                    if formatted_text:
                        page_content.append(formatted_text)
                        page_content.append("")
                    
                    # Check if there's a gap after this block
                    if i < len(text_blocks) - 1:
                        current_block_end = block["y"] + block["height"]
                        next_block_start = text_blocks[i + 1]["y"]
                        if next_block_start - current_block_end > 50:
                            # Insert image in gap if available
                            if image_index < len(image_data):
                                page_content.append(f"![Image]({image_data[image_index]})")
                                page_content.append("")
                                image_index += 1
                
                # Add any remaining images at the end
                while image_index < len(image_data):
                    page_content.append(f"![Image]({image_data[image_index]})")
                    page_content.append("")
                    image_index += 1
                
                # Combine content with proper spacing
                markdown_content.append("\n".join(page_content))
                if page_num < total_pages - 1:
                    markdown_content.append("\n<div style='page-break-after: always;'></div>\n")
                
                print(f"Processed page {page_num + 1}/{total_pages}")
            
            # Write output
            output_path = os.path.join(
                self.output_dir,
                os.path.splitext(os.path.basename(pdf_path))[0] + '.md'
            )
            
            content = "\n".join(markdown_content)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\nConversion complete. Output saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"\nError during conversion: {str(e)}")
            raise


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python converter.py <pdf_file>")
        sys.exit(1)
        
    converter = PDFConverter()
    output_path = converter.convert_pdf(sys.argv[1])
    print(f"Conversion complete. Output saved to: {output_path}")
