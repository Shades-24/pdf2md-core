import re
from typing import List, Dict, Any

class MarkdownAssembler:
    def __init__(self):
        pass
        
    def format_text(self, text: str) -> str:
        """Format text with basic markdown syntax while preserving content."""
        if not text.strip():
            return ""
        
        # Split into lines to handle each separately
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect and format headings
            if line.startswith(('#', '##', '###', '####', '#####', '######')):
                formatted_lines.append(line)
                continue
            
            # Handle inline formatting
            line = re.sub(r'\*\*(.*?)\*\*', r'**\1**', line)  # Bold
            line = re.sub(r'\*(.*?)\*', r'*\1*', line)        # Italic
            line = re.sub(r'`(.*?)`', r'`\1`', line)          # Code
            
            # Add non-empty lines
            if line:
                formatted_lines.append(line)
        
        # Join lines with proper spacing
        return "\n".join(formatted_lines)
