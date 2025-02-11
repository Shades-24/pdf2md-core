import io
import base64
from PIL import Image
from typing import Dict, Any

class ImageProcessor:
    def __init__(self):
        self.max_dimension = 800  # Maximum dimension for image resizing
        
    def image_to_base64(self, image_data: bytes, image_type: str = 'png') -> str:
        """Convert image data to base64 encoded string with optional resizing."""
        try:
            # Load image from bytes
            with Image.open(io.BytesIO(image_data)) as img:
                # Resize if needed while maintaining aspect ratio
                if max(img.size) > self.max_dimension:
                    img.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
                
                # Convert to WebP with aggressive compression
                webp_buffer = io.BytesIO()
                img.save(webp_buffer, 'WEBP', quality=30, method=6, lossless=False)
                webp_buffer.seek(0)
                
                # Base64 encode
                encoded = base64.b64encode(webp_buffer.getvalue()).decode('utf-8')
                return f"data:image/webp;base64,{encoded}"
                
        except Exception as e:
            raise RuntimeError(f"Image processing failed: {str(e)}")
