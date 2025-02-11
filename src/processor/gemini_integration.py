import os
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv
import asyncio
import json
import re

class GeminiProcessor:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self._cache = {}  # Cache for processed pages
        
    async def process_page(self, image_path: str) -> Dict[str, Any]:
        """Process a single PDF page using Gemini Vision API."""
        try:
            # Check cache first
            if image_path in self._cache:
                return self._cache[image_path]
            
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()
                image = {'mime_type': 'image/png', 'data': image_data}
            prompt = """Convert page to markdown. Format:
{
  "markdown": "content with # for headings, * for lists",
  "elements": [
    {"type": "text", "content": "text", "position": {"x": 0, "y": 0}},
    {"type": "heading", "content": "title", "position": {"x": 0, "y": 0}}
  ]
}
Keep structure, lists, tables. Mark images/equations as placeholders."""
            
            response = self.model.generate_content([prompt, image])
            result = self._parse_response(response)
            
            # Cache the result
            self._cache[image_path] = result
            return result
            
        except Exception as e:
            raise RuntimeError(f"Gemini processing failed: {str(e)}")
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse and validate Gemini API response."""
        try:
            # Extract text and attempt to parse as JSON
            text = response.text.strip()
            try:
                # Try to parse as pure JSON first
                data = json.loads(text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from markdown code block
                json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(1))
                else:
                    # Fallback: treat entire response as markdown
                    data = {
                        "markdown": text,
                        "elements": []
                    }
            
            # Validate required fields
            if not isinstance(data, dict):
                raise ValueError("Response must be a dictionary")
            
            if "markdown" not in data:
                data["markdown"] = text
            
            if "elements" not in data:
                data["elements"] = []
                
            return data
            
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")
    
    async def batch_process(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple pages in parallel with optimized batching."""
        chunk_size = 3  # Smaller chunks to avoid rate limiting
        results = []
        
        for i in range(0, len(image_paths), chunk_size):
            chunk = image_paths[i:i + chunk_size]
            tasks = [self.process_page(path) for path in chunk]
            chunk_results = await asyncio.gather(*tasks)
            results.extend(chunk_results)
            
            # Adaptive rate limiting
            if i + chunk_size < len(image_paths):
                await asyncio.sleep(0.2)  # Slightly longer pause between smaller chunks
        
        return results
