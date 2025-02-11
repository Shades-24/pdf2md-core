import os
import re
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv

class GeminiProcessor:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def process_page(self, image_path: str) -> Dict[str, Any]:
        """Process a single PDF page using Gemini Vision API."""
        try:
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()
                image = {'mime_type': 'image/png', 'data': image_data}
            prompt = """
            Convert this PDF page to markdown format. Follow these rules EXACTLY:
            1. The first line MUST start with "# " (hash followed by space) for a level 1 heading
            2. Preserve all text content exactly as it appears
            3. Use blank lines between paragraphs
            4. Remove any trailing whitespace or special characters
            5. Output ONLY the markdown text, no explanations
            
            Required format:
            # Title Here
            
            Paragraph text here.
            
            ## Subheading (if any)
            
            More text here.
            
            IMPORTANT: First line MUST begin with "# " - this is required and non-negotiable.
            """
            
            response = self.model.generate_content([prompt, image])
            print("Debug - Gemini Response:", response.text)  # Debug print
            result = self._parse_response(response)
            print("Debug - Parsed Result:", result)  # Debug print
            return result
        except Exception as e:
            raise RuntimeError(f"Gemini processing failed: {str(e)}")
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse and validate Gemini API response."""
        try:
            # Get the response text and clean it up
            text = response.text.strip()
            if not text:
                text = "# Untitled Document"
            
            # Process the text line by line
            lines = []
            first_line = True
            
            for line in text.split('\n'):
                line = line.strip()
                if line:
                    # Clean any trailing characters
                    line = re.sub(r'[%\s]+$', '', line)
                    # Ensure first line is a heading
                    if first_line:
                        if not line.startswith('# '):
                            line = f"# {line}"
                        first_line = False
                    lines.append(line)
            
            # Ensure we have content
            if not lines:
                lines = ["# Untitled Document"]
            
            # Ensure first line is a heading
            if not lines[0].startswith('# '):
                lines[0] = f"# {lines[0]}"
            
            # Create the markdown content
            markdown_text = '\n\n'.join(lines)
            
            # Create elements with proper types
            elements = []
            for i, line in enumerate(lines):
                element_type = 'heading' if line.startswith('#') else 'text'
                elements.append({
                    "type": element_type,
                    "content": line,
                    "position": {"x": 0, "y": i * 20}
                })
            
            # Return the result
            return {
                "markdown": markdown_text,
                "elements": elements
            }
            
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")
    
    def batch_process(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple pages in parallel."""
        results = []
        for path in image_paths:  # TODO: Implement true parallel processing
            result = self.process_page(path)
            results.append(result)
        return results
