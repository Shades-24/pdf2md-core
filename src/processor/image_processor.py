import io
import base64
from PIL import Image
from typing import Dict, Any, Tuple

class ImageProcessor:
    def __init__(self):
        self.max_dimension = 800  # Maximum dimension for image resizing
        self.min_dimension = 32   # Minimum dimension for small image detection
        self.quality_settings = {
            'diagram': {'quality': 50, 'method': 6, 'lossless': True},  # Better quality for diagrams
            'photo': {'quality': 30, 'method': 6, 'lossless': False},   # More compression for photos
            'icon': {'quality': 60, 'method': 6, 'lossless': True}      # High quality for small icons
        }
        
    def detect_image_type(self, img: Image.Image) -> str:
        """Detect image type based on characteristics."""
        width, height = img.size
        aspect_ratio = width / height
        is_small = max(width, height) <= self.min_dimension
        
        if is_small:
            return 'icon'
        
        # Check if likely a diagram (limited color palette, sharp edges)
        if img.mode in ['1', 'L', 'P'] or len(img.getcolors(maxcolors=256) or []) < 50:
            return 'diagram'
            
        return 'photo'
        
    def optimize_image(self, img: Image.Image, image_type: str) -> Tuple[Image.Image, dict]:
        """Optimize image based on detected type."""
        settings = self.quality_settings[image_type]
        
        # Handle small images
        if image_type == 'icon':
            return img, settings
            
        # Resize larger images while maintaining aspect ratio
        if max(img.size) > self.max_dimension:
            img.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
            
        return img, settings
        
    def image_to_base64(self, image_data: bytes, image_type: str = 'auto') -> str:
        """Convert image data to base64 encoded string with smart optimization."""
        if not image_data:
            raise ValueError("No image data provided")
            
        try:
            # Create a copy of the image data
            image_buffer = io.BytesIO(image_data)
            
            # Load image from buffer
            with Image.open(image_buffer) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode not in ['RGB', 'L']:
                    img = img.convert('RGB')
                
                # Auto-detect image type if not specified
                if image_type == 'auto':
                    image_type = self.detect_image_type(img)
                
                # Optimize image based on type
                optimized_img, settings = self.optimize_image(img, image_type)
                
                # Convert to WebP with type-specific settings
                webp_buffer = io.BytesIO()
                optimized_img.save(webp_buffer, 'WEBP', **settings)
                webp_buffer.seek(0)
                
                # Base64 encode
                encoded = base64.b64encode(webp_buffer.getvalue()).decode('utf-8')
                return f"data:image/webp;base64,{encoded}"
                
        except Image.UnidentifiedImageError:
            raise ValueError("Cannot identify image format")
        except Exception as e:
            raise RuntimeError(f"Image processing failed: {str(e)}")
            
    def process_image(self, image_data: bytes) -> bytes:
        """Process image data with smart optimization."""
        if not image_data:
            raise ValueError("No image data provided")
            
        try:
            # Create a copy of the image data
            image_buffer = io.BytesIO(image_data)
            
            # Load and process image
            with Image.open(image_buffer) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode not in ['RGB', 'L']:
                    img = img.convert('RGB')
                
                # Detect type and optimize
                image_type = self.detect_image_type(img)
                optimized_img, settings = self.optimize_image(img, image_type)
                
                # Save optimized image
                output_buffer = io.BytesIO()
                optimized_img.save(output_buffer, format='WEBP', **settings)
                return output_buffer.getvalue()
                
        except Image.UnidentifiedImageError:
            raise ValueError("Cannot identify image format")
        except Exception as e:
            raise RuntimeError(f"Image processing failed: {str(e)}")
