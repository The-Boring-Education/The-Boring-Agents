"""MDX utilities for formatting interview answers."""

from typing import List
import re


def format_answer_as_mdx(answer: str) -> str:
    """Format answer content as MDX.
    
    Args:
        answer: Raw answer text
        
    Returns:
        MDX-formatted answer
    """
    # Ensure proper header formatting (use #### for section headers)
    answer = _fix_headers(answer)
    
    # Ensure proper code block formatting
    answer = _fix_code_blocks(answer)
    
    # Ensure proper list formatting
    answer = _fix_lists(answer)
    
    # Ensure proper spacing
    answer = _fix_spacing(answer)
    
    return answer


def _fix_headers(content: str) -> str:
    """Fix header formatting to use H4 (####) for consistency.
    
    Args:
        content: Content to fix
        
    Returns:
        Fixed content
    """
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Convert any header level to H4 for consistency
        if line.startswith('# '):
            line = line.replace('# ', '#### ')
        elif line.startswith('## '):
            line = line.replace('## ', '#### ')
        elif line.startswith('### '):
            line = line.replace('### ', '#### ')
        elif line.startswith('##### '):
            # Already H4 or H5, keep as is (some sections might need H5)
            pass
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def _fix_code_blocks(content: str) -> str:
    """Fix code block formatting.
    
    Args:
        content: Content to fix
        
    Returns:
        Fixed content
    """
    # Ensure code blocks have proper language tags
    content = re.sub(r'```\s*\n', '```text\n', content)
    
    # Ensure proper spacing around code blocks
    content = re.sub(r'([^\n])\n(```)', r'\1\n\n\2', content)
    content = re.sub(r'(```[^\n]*)\n([^\n])', r'\1\n\n\2', content)
    
    return content


def _fix_lists(content: str) -> str:
    """Fix list formatting.
    
    Args:
        content: Content to fix
        
    Returns:
        Fixed content
    """
    lines = content.split('\n')
    fixed_lines = []
    in_numbered_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this is a numbered list item
        if re.match(r'^\d+\.\s+', stripped):
            if not in_numbered_list:
                # Starting a new numbered list, add blank line before if needed
                if fixed_lines and fixed_lines[-1].strip():
                    fixed_lines.append('')
                in_numbered_list = True
            fixed_lines.append(line)
        else:
            if stripped == '':
                in_numbered_list = False
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def _fix_spacing(content: str) -> str:
    """Fix spacing to ensure proper breathable space between sections.
    
    Args:
        content: Content to fix
        
    Returns:
        Fixed content
    """
    # Add proper spacing between H4 sections and content
    content = re.sub(r'(####\s+[^\n]+)\n([^\n])', r'\1\n\n\n\2', content)
    
    # Add proper spacing before H4 sections (except the first one)
    content = re.sub(r'([^\n])\n(####\s+[^\n]+)', r'\1\n\n\n\2', content)
    
    # Ensure code blocks have proper spacing
    content = re.sub(r'([^\n])\n(```)', r'\1\n\n\2', content)
    content = re.sub(r'(```[^\n]*)\n([^\n])', r'\1\n\n\2', content)
    
    # Add spacing around numbered lists
    content = re.sub(r'([^\n])\n(1\.)', r'\1\n\n\2', content)
    content = re.sub(r'(\d+\.\s+[^\n]+)\n([^\n\d])', r'\1\n\n\2', content)
    
    # Clean up excessive spacing (more than 3 consecutive blank lines)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    return content


def validate_mdx_structure(content: str) -> tuple[bool, List[str]]:
    """Validate MDX structure.
    
    Args:
        content: MDX content to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check for balanced code blocks
    code_block_count = content.count('```')
    if code_block_count % 2 != 0:
        errors.append("Unbalanced code blocks (missing closing ```)")
    
    # Check for proper header structure
    headers = re.findall(r'^#{1,6}\s+', content, re.MULTILINE)
    if not headers:
        errors.append("No headers found in content")
    
    return len(errors) == 0, errors

