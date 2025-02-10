import os
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
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
    async def process_page(self, image_path: str) -> Dict[str, Any]:
        """Process a single PDF page using Gemini Vision API."""
        try:
            image = genai.types.Image.from_file(image_path)
            prompt = """
            Analyze this PDF page and convert it to markdown format. Pay special attention to:
            1. Heading levels (h1, h2, etc.)
            2. Text formatting (bold, italic)
            3. Lists and tables
            4. Mathematical equations
            5. Image/diagram placement
            
            Return a JSON object with:
            {
                "markdown": "converted markdown text",
                "elements": [
                    {
                        "type": "text/heading/image/equation/table",
                        "content": "element content",
                        "position": {"x": int, "y": int}
                    }
                ]
            }
            """
            
            response = await self.model.generate_content([prompt, image])
            return self._parse_response(response)
        except Exception as e:
            raise RuntimeError(f"Gemini processing failed: {str(e)}")
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse and validate Gemini API response."""
        try:
            result = response.text
            # TODO: Add response validation and cleanup
            return {
                "markdown": result,
                "elements": []  # Parse structured elements from response
            }
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")
    
    async def batch_process(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple pages in parallel."""
        results = []
        for path in image_paths:  # TODO: Implement true parallel processing
            result = await self.process_page(path)
            results.append(result)
        return results
