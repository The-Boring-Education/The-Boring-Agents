"""MDX Styling Agent for improving the formatting and readability of interview answers."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
import re

from ...core.base_agent import BaseAgent


class MDXStylingAgent(BaseAgent):
    """Agent for improving MDX formatting and readability of interview answers."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for MDX styling."""
        
        mdx_formatting_template = PromptTemplate(
            input_variables=["content", "content_type_param"],
            template="""
            You are an expert MDX content formatter specializing in technical interview content.
            
            **Content to Format:** {content}
            **Content Type:** {content_type_param}
            
            Format this content with STRICT adherence to these formatting rules:
            
            ## CRITICAL FORMATTING REQUIREMENTS:
            
            ### Headers and Spacing
            - Use H4 (####) for ALL section headers - NO EXCEPTIONS
            - Add exactly TWO blank lines after each section heading
            - Add exactly TWO blank lines before each new section heading
            - Keep headers concise and descriptive with emojis
            
            ### Numbered Lists
            - Use proper numbered format: "1.", "2.", "3." with a space after the period
            - Each list item should be on its own line
            - Add blank line before starting any numbered list
            - For sub-points, use proper indentation with "   a.", "   b.", etc.
            
            ### Code Blocks
            - Use proper language tags (```javascript, ```python, etc.)
            - Add comments to explain complex code
            - Use inline code (`code`) for short snippets
            - Format code blocks with proper indentation
            - Add blank lines before and after code blocks
            
            ### Content Structure
            - Every section must have substantial content - no placeholder text
            - Use consistent spacing throughout
            - Ensure readability with proper line breaks
            - Make lists visually clear and scannable
            
            ### Quality Standards
            - Content should be engaging and professional
            - Use emojis strategically for section headers
            - Maintain consistent tone throughout
            - Ensure technical accuracy in all examples
            
            ## SPECIFIC FORMATTING EXAMPLE:
            
            #### 🎯 Quick Answer
            
            
            This is the content for quick answer section.
            
            
            #### 📖 Introduction
            
            
            This is the introduction content.
            
            
            #### 🧠 Practice Problems
            
            
            1. First problem description that is specific and actionable
            2. Second problem description that is specific and actionable
            3. Third problem description that is specific and actionable
            
            
            #### 💼 Interview Pro Tips
            
            
            **What interviewers want to hear:**
            
            1. First key point they want to hear
            2. Second key point they want to hear
            3. Third key point they want to hear
            
            **Red flags to avoid:**
            
            1. First thing to avoid saying
            2. Second thing to avoid saying
            3. Third thing to avoid saying
            
            
            ## VALIDATION CHECKLIST:
            Before returning the content, verify:
            ✓ All headers use #### format
            ✓ Two blank lines after each header
            ✓ Two blank lines before each new section
            ✓ Numbered lists use "1.", "2.", "3." format
            ✓ No "Related Concepts to Revise" section
            ✓ "Tips or Tricks" is renamed to "Tip"
            ✓ Content is substantial and valuable
            ✓ Proper spacing throughout
            
            Return the properly formatted MDX content that strictly follows these rules.
            """
        )
        
        readability_improvement_template = PromptTemplate(
            input_variables=["content"],
            template="""
            Improve the readability of this MDX content:
            
            **Original Content:** {content}
            
            Focus on:
            1. **Clear Section Headers** - Make them descriptive and engaging
            2. **Proper Code Formatting** - Ensure code blocks are well-formatted
            3. **Consistent Spacing** - Add proper breaks between sections
            4. **Visual Hierarchy** - Use headers, lists, and formatting effectively
            5. **Engagement Elements** - Add formatting that makes content more engaging
            
            Return the improved content with better readability and formatting.
            """
        )
        
        return {
            "mdx_formatting": mdx_formatting_template,
            "readability_improvement": readability_improvement_template
        }
    
    def format_mdx_content(self, content: str, content_type: str = "interview_answer") -> str:
        """Format content with proper MDX styling.
        
        Args:
            content: Raw content to format
            content_type: Type of content (interview_answer, course_content, etc.)
            
        Returns:
            Properly formatted MDX content
        """
        result = self.generate_content(
            content_type="mdx_formatting",
            content=content,
            content_type_param=content_type
        )
        
        return result["generated_content"]
    
    def improve_readability(self, content: str) -> str:
        """Improve the readability of existing MDX content.
        
        Args:
            content: Existing MDX content
            
        Returns:
            Improved MDX content
        """
        result = self.generate_content(
            content_type="readability_improvement",
            content=content
        )
        
        return result["generated_content"]
    
    def apply_consistent_styling(self, content: str) -> str:
        """Apply consistent styling rules to MDX content.
        
        Args:
            content: MDX content to style
            
        Returns:
            Consistently styled content
        """
        # Apply basic formatting rules
        content = self._fix_headers(content)
        content = self._fix_code_blocks(content)
        content = self._fix_lists(content)
        content = self._fix_spacing(content)
        content = self._add_visual_elements(content)
        
        return content
    
    def _fix_headers(self, content: str) -> str:
        """Fix header formatting to use H4 and ensure proper structure."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Convert any header level to H4 for consistency
            if line.startswith('# '):
                # Convert H1 to H4
                line = line.replace('# ', '#### ')
            elif line.startswith('## '):
                # Convert H2 to H4
                line = line.replace('## ', '#### ')
            elif line.startswith('### '):
                # Convert H3 to H4
                line = line.replace('### ', '#### ')
            elif line.startswith('#### '):
                # Already H4, keep as is
                pass
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_code_blocks(self, content: str) -> str:
        """Fix code block formatting."""
        # Ensure code blocks have proper language tags
        content = re.sub(r'```\n', '```javascript\n', content)
        content = re.sub(r'```\s*\n', '```javascript\n', content)
        
        # Add comments to code blocks if missing
        code_block_pattern = r'```(\w+)\n(.*?)```'
        
        def add_comments(match):
            language = match.group(1)
            code = match.group(2)
            
            if not code.strip().startswith('//') and not code.strip().startswith('#'):
                # Add a comment if no comments exist
                if language == 'javascript':
                    code = f'// {language.title()} code example\n{code}'
                elif language == 'python':
                    code = f'# {language.title()} code example\n{code}'
            
            return f'```{language}\n{code}```'
        
        content = re.sub(code_block_pattern, add_comments, content, flags=re.DOTALL)
        
        return content
    
    def _fix_lists(self, content: str) -> str:
        """Fix list formatting to ensure proper numbered lists."""
        lines = content.split('\n')
        fixed_lines = []
        in_numbered_list = False
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Check if this is a numbered list item
            if stripped_line and (stripped_line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or 
                                 stripped_line.startswith(tuple(f'{j}.' for j in range(10, 100)))):
                if not in_numbered_list:
                    # Starting a new numbered list, add blank line before if needed
                    if fixed_lines and fixed_lines[-1].strip():
                        fixed_lines.append('')
                    in_numbered_list = True
                
                # Ensure proper format: "1. Content"
                if '. ' not in stripped_line:
                    stripped_line = stripped_line.replace('.', '. ', 1)
                fixed_lines.append(stripped_line)
            
            # Check if this is a bullet point that should be numbered
            elif stripped_line.startswith('- ') and in_numbered_list:
                # Convert bullet to number (this is a simple approach)
                list_number = len([l for l in fixed_lines if l.strip() and 
                                 any(l.strip().startswith(f'{j}.') for j in range(1, 100))]) + 1
                content = stripped_line[2:].strip()  # Remove "- "
                fixed_lines.append(f"{list_number}. {content}")
            
            else:
                if stripped_line == '':
                    in_numbered_list = False
                elif not stripped_line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) and \
                     not stripped_line.startswith(tuple(f'{j}.' for j in range(10, 100))):
                    in_numbered_list = False
                
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_spacing(self, content: str) -> str:
        """Fix spacing to ensure proper breathable space between sections."""
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
    
    def _add_visual_elements(self, content: str) -> str:
        """Add visual elements for better engagement."""
        # Add dividers between major sections
        major_sections = [
            'Quick Answer', 'Introduction', 'Code Example', 'Why This Concept Matters',
            'Different Ways Interviewers Ask This', 'Bad Code Example', 'Good Code Example',
            'Related Concepts to Revise', 'Cliffhanger', 'Memory Trick', 'Pro Tips',
            'Career Impact', 'Companies That Ask This', 'Practice Scenarios', 'Follow-up Questions'
        ]
        
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # Add divider after major sections
            if any(section in line for section in major_sections) and line.startswith('## '):
                if i < len(lines) - 1 and not lines[i + 1].strip().startswith('---'):
                    fixed_lines.append('')
                    fixed_lines.append('---')
                    fixed_lines.append('')
        
        return '\n'.join(fixed_lines)
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate formatted content based on the content type."""
        if content_type not in self.prompt_templates:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Format the prompt
        prompt = self._format_prompt(content_type, **kwargs)
        
        # Generate content
        generated_content = self._generate_with_prompt(prompt)
        
        return {
            "generated_content": generated_content,
            "content_type": content_type,
            "parameters": kwargs
        } 