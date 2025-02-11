import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Heading:
    text: str
    level: int
    position: int
    font_size: float = None
    is_bold: bool = False
    
class HeadingProcessor:
    def __init__(self):
        self.min_heading_length = 3  # Minimum length for a heading
        self.max_heading_length = 200  # Maximum length for a heading
        self.heading_patterns = [
            r'^#{1,6}\s+.+$',  # Markdown style
            r'^(\d+\.)+\s+.+$',  # Numbered style
            r'^[A-Z][A-Za-z\s]+:',  # Title style
            r'^[A-Z][A-Z\s]+[A-Z]$'  # All caps style
        ]
        
    def detect_heading_level(self, text: str, font_size: float = None, 
                           is_bold: bool = False, prev_headings: List[Heading] = None) -> int:
        """Determine the appropriate heading level."""
        if not text or len(text) < self.min_heading_length or len(text) > self.max_heading_length:
            return 0
            
        # Check if it matches any heading patterns
        is_heading_pattern = any(re.match(pattern, text) for pattern in self.heading_patterns) or re.match(r'^\d+(?:\.\d+)*\.?\s+.+$', text)
        
        if font_size is not None:
            # Use font size to determine heading level
            if font_size >= 20:
                return 1
            elif font_size >= 16:
                return 2
            elif font_size >= 14:
                return 3
            elif font_size >= 12 and is_bold:
                return 4
        
        # Use pattern matching if no font size info
        if is_heading_pattern:
            # Check numbered pattern depth (e.g., 1.2.3)
            if re.match(r'^\d+(?:\.\d+)*\.?\s+.+$', text):
                # Count the number of numbers
                numbers = re.findall(r'\d+', text.split()[0])
                return min(len(numbers), 6)
            # Check markdown style depth
            elif match := re.match(r'^(#{1,6})\s+.+$', text):
                return len(match.group(1))
            # Check title case with colon
            elif re.match(r'^[A-Z][A-Za-z\s]+:', text):
                return 2
            # Check all caps
            elif text.isupper() and len(text.split()) <= 4:
                return 2
            # Other patterns default to level 3
            return 3
            
        return 0
        
    def normalize_heading_levels(self, headings: List[Heading]) -> List[Heading]:
        """Ensure heading levels are properly nested."""
        if not headings:
            return headings
            
        # Create a map of original levels
        level_map = {heading.level: [] for heading in headings}
        for heading in headings:
            level_map[heading.level].append(heading)
            
        # Sort levels in ascending order
        sorted_levels = sorted(level_map.keys())
        
        # Create new level mapping
        new_level_map = {}
        for i, level in enumerate(sorted_levels, 1):
            new_level_map[level] = min(i, 6)  # Cap at h6
            
        # Update heading levels
        for heading in headings:
            heading.level = new_level_map[heading.level]
            
        return headings
        
    def extract_headings(self, text: str, font_info: Dict[int, Tuple[float, bool]] = None) -> List[Heading]:
        """Extract headings from text with their levels."""
        headings = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Get font info if available
            font_size = None
            is_bold = False
            if font_info and i in font_info:
                font_size, is_bold = font_info[i]
                
            # Detect heading level
            level = self.detect_heading_level(
                line, 
                font_size, 
                is_bold,
                headings
            )
            
            if level > 0:
                headings.append(Heading(
                    text=line,
                    level=level,
                    position=i,
                    font_size=font_size,
                    is_bold=is_bold
                ))
                
        return self.normalize_heading_levels(headings)
        
    def convert_to_markdown(self, text: str, font_info: Dict[int, Tuple[float, bool]] = None) -> str:
        """Convert headings to proper markdown format."""
        if not text:
            return text
            
        headings = self.extract_headings(text, font_info)
        if not headings:
            return text
            
        lines = text.split('\n')
        result = []
        
        # Track processed headings
        heading_positions = {h.position: h for h in headings}
        
        # Process each line
        for i, line in enumerate(lines):
            if i in heading_positions:
                heading = heading_positions[i]
                # Clean heading text
                clean_text = re.sub(r'^[\d\.#\s]+', '', line.strip())
                clean_text = re.sub(r':$', '', clean_text)
                # Add markdown heading
                result.append(f"{'#' * heading.level} {clean_text}")
            else:
                result.append(line)
                
        return '\n'.join(result)
        
    def get_table_of_contents(self, headings: List[Heading]) -> str:
        """Generate a table of contents from headings."""
        if not headings:
            return ""
            
        toc = ["# Table of Contents\n"]
        
        for heading in headings:
            # Calculate indent based on level
            indent = "  " * (heading.level - 1)
            # Clean heading text
            clean_text = re.sub(r'^[\d\.#\s]+', '', heading.text.strip())
            clean_text = re.sub(r':$', '', clean_text)
            # Create anchor link
            anchor = clean_text.lower().replace(' ', '-')
            anchor = re.sub(r'[^\w\-]', '', anchor)
            # Add TOC entry
            toc.append(f"{indent}- [{clean_text}](#{anchor})")
            
        return '\n'.join(toc)
