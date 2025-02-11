from typing import List, Dict, Optional

class MarkdownAssembler:
    def __init__(self):
        self.image_template = "![{alt}]({src})"
        
    def assemble(self, text: str, images: List[Dict], toc: Optional[str] = None) -> str:
        """Assemble the final markdown document."""
        parts = []
        
        # Add table of contents if provided
        if toc:
            parts.append(toc)
            parts.append("\n---\n")  # Separator after TOC
            
        # Process text and insert images at their positions
        current_pos = 0
        text_parts = []
        
        # Handle case where images is None
        if not images:
            parts.append(text)
            return '\n\n'.join(parts)
            
        try:
            # Sort images by position
            sorted_images = sorted(
                [img for img in images if isinstance(img, dict) and 'position' in img and 'data' in img],
                key=lambda x: x['position']
            )
            
            for img in sorted_images:
                try:
                    # Add text up to image position
                    text_parts.append(text[current_pos:img['position']])
                    
                    # Add image markdown with error handling
                    try:
                        image_md = self.image_template.format(
                            alt=f"Image at position {img['position']}",
                            src=img.get('data', '[Image processing failed]')
                        )
                        text_parts.append(f"\n\n{image_md}\n\n")
                    except Exception as e:
                        print(f"Warning: Failed to format image: {e}")
                        text_parts.append("\n\n[Image processing failed]\n\n")
                        
                    current_pos = img['position']
                except Exception as e:
                    print(f"Warning: Failed to process image at position {img.get('position', 'unknown')}: {e}")
                    continue
                    
            # Add remaining text
            text_parts.append(text[current_pos:])
            
        except Exception as e:
            print(f"Warning: Failed to process images: {e}")
            # Fall back to just the text
            text_parts = [text]
            
        # Join text parts
        parts.append(''.join(text_parts))
        
        return '\n\n'.join(parts)
