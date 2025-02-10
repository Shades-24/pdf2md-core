import os
import fitz
import pytesseract
from PIL import Image
from typing import List, Dict, Tuple
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ImageProcessor:
    def __init__(self, dpi: int = 300):
        self.dpi = dpi
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def pdf_to_images(self, pdf_path: str) -> List[str]:
        """Convert PDF pages to images."""
        temp_dir = tempfile.mkdtemp(prefix='pdf2md_')
        image_paths = []
        
        try:
            doc = fitz.open(pdf_path)
            tasks = []
            
            for page_num in range(len(doc)):
                task = self._process_page(doc[page_num], temp_dir, page_num)
                tasks.append(task)
            
            image_paths = await asyncio.gather(*tasks)
            return sorted(image_paths)  # Ensure correct page order
            
        except Exception as e:
            raise RuntimeError(f"PDF to image conversion failed: {str(e)}")
    
    async def _process_page(self, page, temp_dir: str, page_num: int) -> str:
        """Process a single PDF page to image."""
        try:
            # Get page as image
            pix = page.get_pixmap(matrix=fitz.Matrix(self.dpi/72, self.dpi/72))
            image_path = os.path.join(temp_dir, f'page_{page_num:03d}.png')
            
            # Save image
            pix.save(image_path)
            
            # Extract any embedded images
            image_list = page.get_images(full=True)
            if image_list:
                await self._extract_embedded_images(page, image_list, temp_dir, page_num)
            
            return image_path
            
        except Exception as e:
            raise RuntimeError(f"Page processing failed: {str(e)}")
    
    async def _extract_embedded_images(self, page, image_list: List, temp_dir: str, page_num: int):
        """Extract embedded images from PDF page."""
        doc = page.parent
        for img_idx, img_info in enumerate(image_list):
            try:
                base_image = doc.extract_image(img_info[0])
                if base_image:
                    image_path = os.path.join(
                        temp_dir, 
                        f'embedded_p{page_num:03d}_i{img_idx:03d}.{base_image["ext"]}'
                    )
                    with open(image_path, 'wb') as img_file:
                        img_file.write(base_image["image"])
            except Exception as e:
                print(f"Warning: Failed to extract embedded image: {str(e)}")
    
    async def perform_ocr(self, image_path: str) -> Dict[str, Any]:
        """Perform OCR on image using Tesseract."""
        try:
            loop = asyncio.get_event_loop()
            # Run OCR in thread pool to avoid blocking
            result = await loop.run_in_executor(
                self.executor,
                self._run_tesseract,
                image_path
            )
            return result
        except Exception as e:
            raise RuntimeError(f"OCR failed: {str(e)}")
    
    def _run_tesseract(self, image_path: str) -> Dict[str, Any]:
        """Run Tesseract OCR on image."""
        try:
            image = Image.open(image_path)
            # Get text and bounding boxes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Process results
            result = {
                "text": [],
                "boxes": []
            }
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 60:  # Filter low confidence results
                    result['text'].append(data['text'][i])
                    result['boxes'].append({
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'w': data['width'][i],
                        'h': data['height'][i]
                    })
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Tesseract processing failed: {str(e)}")
    
    def cleanup(self, temp_dir: str):
        """Clean up temporary files."""
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Warning: Cleanup failed: {str(e)}")
