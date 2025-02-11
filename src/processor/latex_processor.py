import re
from typing import List, Tuple

class LatexProcessor:
    def __init__(self):
        # Regex patterns for different LaTeX elements
        self.block_equation_pattern = r'\\begin\{equation\}(.*?)\\end\{equation\}'
        self.inline_equation_pattern = r'\$(.*?)\$'
        self.align_pattern = r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}'
        
    def detect_latex(self, text: str) -> bool:
        """Check if text contains LaTeX equations."""
        patterns = [
            self.block_equation_pattern,
            self.inline_equation_pattern,
            self.align_pattern
        ]
        return any(re.search(pattern, text, re.DOTALL) for pattern in patterns)
    
    def extract_equations(self, text: str) -> List[Tuple[str, str, int, int]]:
        """Extract LaTeX equations with their positions."""
        equations = []
        
        # Find block equations
        for match in re.finditer(self.block_equation_pattern, text, re.DOTALL):
            equations.append((
                match.group(1).strip(),
                'block',
                match.start(),
                match.end()
            ))
            
        # Find inline equations
        for match in re.finditer(self.inline_equation_pattern, text):
            equations.append((
                match.group(1).strip(),
                'inline',
                match.start(),
                match.end()
            ))
            
        # Find align environments
        for match in re.finditer(self.align_pattern, text, re.DOTALL):
            equations.append((
                match.group(1).strip(),
                'align',
                match.start(),
                match.end()
            ))
            
        return sorted(equations, key=lambda x: x[2])  # Sort by position
    
    def clean_equation(self, equation: str) -> str:
        """Clean and normalize LaTeX equation."""
        # Remove unnecessary whitespace
        equation = re.sub(r'\s+', ' ', equation.strip())
        
        # Normalize common LaTeX commands
        replacements = [
            (r'\\left', ''),
            (r'\\right', ''),
            (r'\\begin\{array\}', r'\\begin{aligned}'),
            (r'\\end\{array\}', r'\\end{aligned}'),
            (r'\\begin\{matrix\}', r'\\begin{aligned}'),
            (r'\\end\{matrix\}', r'\\end{aligned}')
        ]
        
        for old, new in replacements:
            equation = re.sub(old, new, equation)
            
        return equation
    
    def convert_to_markdown(self, text: str) -> str:
        """Convert LaTeX equations in text to markdown format."""
        if not self.detect_latex(text):
            return text
            
        equations = self.extract_equations(text)
        result = text
        offset = 0
        
        for eq, eq_type, start, end in equations:
            cleaned_eq = self.clean_equation(eq)
            
            if eq_type == 'block':
                # Block equations use double dollar signs
                markdown_eq = f"\n$$\n{cleaned_eq}\n$$\n"
            elif eq_type == 'align':
                # Align environments also use double dollar signs
                markdown_eq = f"\n$$\n\\begin{{aligned}}\n{cleaned_eq}\n\\end{{aligned}}\n$$\n"
            else:
                # Inline equations use single dollar signs
                markdown_eq = f"${cleaned_eq}$"
                
            # Replace equation in text, accounting for previous replacements
            result = (
                result[:start + offset] +
                markdown_eq +
                result[end + offset:]
            )
            offset += len(markdown_eq) - (end - start)
            
        return result
