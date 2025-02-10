import re
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ElementType(Enum):
    TEXT = "text"
    HEADING = "heading"
    IMAGE = "image"
    EQUATION = "equation"
    TABLE = "table"
    LIST = "list"

@dataclass
class Element:
    type: ElementType
    content: str
    position: Dict[str, int]
    metadata: Dict[str, Any] = None

class MarkdownAssembler:
    def __init__(self):
        self.current_heading_level = 0
        self.list_stack = []
        
    def assemble_document(self, pages: List[Dict[str, Any]]) -> str:
        """Assemble full markdown document from processed pages."""
        markdown_content = []
        
        for page_num, page in enumerate(pages):
            page_content = self._process_page(page, page_num)
            markdown_content.append(page_content)
        
        return "\n\n".join(markdown_content)
    
    def _process_page(self, page: Dict[str, Any], page_num: int) -> str:
        """Process a single page's elements into markdown."""
        elements = self._sort_elements(page.get('elements', []))
        markdown_lines = []
        
        for element in elements:
            processed = self._process_element(Element(
                type=ElementType(element['type']),
                content=element['content'],
                position=element.get('position', {'x': 0, 'y': 0}),
                metadata=element.get('metadata', {})
            ))
            if processed:
                markdown_lines.append(processed)
        
        return "\n".join(markdown_lines)
    
    def _sort_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort elements by vertical position and hierarchy."""
        return sorted(elements, key=lambda x: (
            x.get('position', {}).get('y', 0),
            self._get_element_priority(x['type'])
        ))
    
    def _get_element_priority(self, element_type: str) -> int:
        """Get priority for element type (lower = higher priority)."""
        priorities = {
            'heading': 0,
            'text': 1,
            'list': 2,
            'table': 3,
            'equation': 4,
            'image': 5
        }
        return priorities.get(element_type, 99)
    
    def _process_element(self, element: Element) -> str:
        """Convert element to markdown format."""
        processors = {
            ElementType.TEXT: self._process_text,
            ElementType.HEADING: self._process_heading,
            ElementType.IMAGE: self._process_image,
            ElementType.EQUATION: self._process_equation,
            ElementType.TABLE: self._process_table,
            ElementType.LIST: self._process_list
        }
        
        processor = processors.get(element.type)
        if processor:
            return processor(element)
        return ""
    
    def _process_text(self, element: Element) -> str:
        """Process plain text, preserving formatting."""
        text = element.content.strip()
        if not text:
            return ""
            
        # Handle inline formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'*\1*', text)        # Italic
        text = re.sub(r'`(.*?)`', r'`\1`', text)          # Code
        
        return text
    
    def _process_heading(self, element: Element) -> str:
        """Process heading with proper level."""
        level = element.metadata.get('level', 1)
        self.current_heading_level = level
        return f"{'#' * level} {element.content.strip()}"
    
    def _process_image(self, element: Element) -> str:
        """Process image with alt text and path."""
        alt_text = element.metadata.get('alt_text', 'Image')
        path = element.content
        return f"![{alt_text}]({path})"
    
    def _process_equation(self, element: Element) -> str:
        """Process mathematical equations."""
        is_inline = element.metadata.get('inline', False)
        equation = element.content.strip()
        
        if is_inline:
            return f"${equation}$"
        return f"$${equation}$$"
    
    def _process_table(self, element: Element) -> str:
        """Process tables with alignment."""
        if isinstance(element.content, str):
            return element.content  # Already formatted table
            
        rows = element.content
        if not rows:
            return ""
            
        # Create header
        header = " | ".join(rows[0])
        separator = " | ".join(['---'] * len(rows[0]))
        
        # Create body
        body = []
        for row in rows[1:]:
            body.append(" | ".join(row))
            
        return f"| {header} |\n| {separator} |\n" + \
               "\n".join(f"| {row} |" for row in body)
    
    def _process_list(self, element: Element) -> str:
        """Process nested lists."""
        level = element.metadata.get('level', 0)
        is_ordered = element.metadata.get('ordered', False)
        
        # Adjust list stack
        while len(self.list_stack) > level:
            self.list_stack.pop()
        while len(self.list_stack) < level:
            self.list_stack.append(is_ordered)
            
        prefix = "  " * level
        marker = f"{len(self.list_stack)}." if is_ordered else "-"
        
        return f"{prefix}{marker} {element.content.strip()}"
