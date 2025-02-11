import re
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class Footnote:
    id: str
    content: str
    reference_pos: int
    content_pos: int

class FootnoteProcessor:
    def __init__(self):
        # Regex patterns for footnotes
        self.footnote_ref_pattern = r'\[(\d+|\*)\]'  # Matches [1] or [*]
        self.footnote_content_pattern = r'^\s*(?:(\d+)\.|\*)\s+(.+?)(?=\n\s*(?:\d+\.|\*)\s+|\Z)'
        self.footnote_markers = ['*', '†', '‡', '§']
        
    def is_likely_footnote_section(self, text: str, y_position: float, page_height: float) -> bool:
        """Determine if text block is likely a footnote section based on position and content."""
        # Check if text is in bottom third of page
        if y_position < page_height * 0.7:
            return False
            
        # Check if text starts with common footnote markers
        first_line = text.split('\n')[0].strip()
        return bool(re.match(r'(?:\d+[\.\)]|[\*†‡§])\s+', first_line))
        
    def extract_footnotes(self, text: str, y_position: float = None, page_height: float = None) -> List[Footnote]:
        """Extract footnotes from text."""
        footnotes = []
        
        # First pass: find all footnote references
        references = [(m.group(1) if m.group(1) else '*', m.start()) 
                     for m in re.finditer(self.footnote_ref_pattern, text)]
        
        # Second pass: find footnote content
        content_matches = re.finditer(self.footnote_content_pattern, text, re.MULTILINE)
        
        # Match references with content
        ref_dict: Dict[str, List[int]] = {}  # id -> list of positions
        for ref_id, pos in references:
            if ref_id not in ref_dict:
                ref_dict[ref_id] = []
            ref_dict[ref_id].append(pos)
            
        # Process footnote content
        for match in re.finditer(self.footnote_content_pattern, text, re.MULTILINE):
            content = match.group(2).strip() if match.group(2) else match.group(1).strip()
            content_pos = match.start()
            
            # Determine footnote ID
            footnote_id = match.group(1) if match.group(1) else '*'
            
            # Add footnote for each reference
            if footnote_id in ref_dict:
                for ref_pos in ref_dict[footnote_id]:
                    footnotes.append(Footnote(
                        id=footnote_id,
                        content=content,
                        reference_pos=ref_pos,
                        content_pos=content_pos
                    ))
                
        return sorted(footnotes, key=lambda f: f.reference_pos)
        
    def convert_to_markdown(self, text: str, y_position: float = None, page_height: float = None) -> str:
        """Convert footnotes to markdown format."""
        if not text:
            return text
            
        footnotes = self.extract_footnotes(text, y_position, page_height)
        if not footnotes:
            return text
            
        result = text
        offset = 0
        footnote_section = "\n\n---\n"  # Horizontal rule before footnotes
        
        # Process footnotes in reverse order to maintain positions
        for footnote in reversed(footnotes):
            # Replace reference with markdown reference
            ref_markdown = f"[^{footnote.id}]"
            result = (
                result[:footnote.reference_pos + offset] +
                ref_markdown +
                result[footnote.reference_pos + len(footnote.id) + 2 + offset:]
            )
            offset += len(ref_markdown) - (len(footnote.id) + 2)
            
            # Add footnote content to footnote section
            footnote_section += f"\n[^{footnote.id}]: {footnote.content}"
            
        # Remove original footnote content and add markdown footnotes at the end
        result = re.sub(self.footnote_content_pattern, '', result, flags=re.MULTILINE)
        result = result.strip() + footnote_section
        
        return result
        
    def merge_footnotes(self, texts: List[str]) -> str:
        """Merge footnotes from multiple text blocks/pages."""
        all_footnotes: Dict[str, str] = {}
        processed_texts = []
        
        # First pass: collect all footnotes
        for text in texts:
            footnotes = self.extract_footnotes(text)
            for footnote in footnotes:
                if footnote.id not in all_footnotes:
                    all_footnotes[footnote.id] = footnote.content
                    
        # Second pass: process each text block
        for text in texts:
            processed = self.convert_to_markdown(text)
            processed_texts.append(processed)
            
        # Combine texts and add merged footnotes
        result = "\n\n".join(processed_texts)
        
        # Add merged footnote section if there are footnotes
        if all_footnotes:
            result += "\n\n---\n"
            for footnote_id, content in sorted(all_footnotes.items()):
                result += f"\n[^{footnote_id}]: {content}"
                
        return result
