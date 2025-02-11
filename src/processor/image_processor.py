import os
import fitz
import base64
from PIL import Image
from typing import List, Dict, Any
import tempfile
import io

class ImageProcessor:
    def __init__(self, dpi: int = 300):
        self.dpi = dpi
        
    def extract_images(self, page: fitz.Page, temp_dir: str) -> List[Dict[str, Any]]:
        """Extract images from a PDF page."""
        images = []
        
        try:
            # Get page dimensions
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Extract image blocks
            blocks = page.get_text("dict")["blocks"]
            for block_idx, block in enumerate(blocks):
                if block["type"] == 1:  # Image block
                    try:
                        # Get image rectangle
                        bbox = block["bbox"]
                        rect = fitz.Rect(bbox)
                        
                        # Add some padding to capture full image
                        padding = 2  # pixels
                        rect.x0 = max(0, rect.x0 - padding)
                        rect.y0 = max(0, rect.y0 - padding)
                        rect.x1 = min(page_width, rect.x1 + padding)
                        rect.y1 = min(page_height, rect.y1 + padding)
                        
                        # Render page region to pixmap with high resolution
                        zoom = self.dpi / 72  # Convert DPI to zoom factor
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
                        
                        # Save pixmap to temp file
                        img_path = os.path.join(temp_dir, f'block_{block_idx}.png')
                        pix.save(img_path)
                        
                        # Optimize image
                        self.optimize_image(img_path)
                        
                        # Convert to base64
                        with open(img_path, 'rb') as img_file:
                            img_data = img_file.read()
                            img_b64 = base64.b64encode(img_data).decode('utf-8')
                            
                        # Add to images list
                        images.append({
                            'data': f"data:image/png;base64,{img_b64}",
                            'x': bbox[0] / page_width,
                            'y': bbox[1] / page_height,
                            'width': (bbox[2] - bbox[0]) / page_width,
                            'height': (bbox[3] - bbox[1]) / page_height,
                            'alt': f"Image {block_idx + 1}"
                        })
                        
                    except Exception as e:
                        print(f"Warning: Failed to extract image block: {str(e)}")
                        continue
                        
            return images
            
        except Exception as e:
            print(f"Warning: Failed to extract images from page: {str(e)}")
            return []
            
    def optimize_image(self, img_path: str, max_size: int = 800) -> None:
        """Optimize image size while maintaining quality."""
        try:
            with Image.open(img_path) as img:
                # Convert to RGB if needed
                if img.mode in ['RGBA', 'LA']:
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])
                    else:
                        background.paste(img, mask=img.split()[1])
                    img = background
                elif img.mode not in ['RGB', 'L']:
                    img = img.convert('RGB')
                
                # Check if resize needed
                if max(img.size) > max_size:
                    # Calculate new size maintaining aspect ratio
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    # Resize with high quality
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(img_path, 'PNG', optimize=True)
                
        except Exception as e:
            print(f"Warning: Failed to optimize image: {str(e)}")
            
    def cleanup(self, temp_dir: str) -> None:
        """Clean up temporary files."""
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Warning: Cleanup failed: {str(e)}")
