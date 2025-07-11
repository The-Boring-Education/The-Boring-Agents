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
            
            Format this content with proper MDX styling that is:
            1. **Highly Readable** - Clear hierarchy and structure
            2. **Visually Appealing** - Good use of formatting elements
            3. **Professional** - Suitable for educational content
            4. **Engaging** - Uses formatting to enhance engagement
            
            ## Formatting Rules:
            
            ### Headers
            - Use H2 (##) for main sections
            - Use H3 (###) for subsections
            - Use H4 (####) for minor sections
            - Keep headers concise and descriptive
            
            ### Code Blocks
            - Use proper language tags (```javascript, ```python, etc.)
            - Add comments to explain complex code
            - Use inline code (`code`) for short snippets
            - Format code blocks with proper indentation
            
            ### Lists
            - Use numbered lists for sequential steps
            - Use bullet points for related items
            - Use nested lists for sub-items
            - Keep list items concise
            
            ### Emphasis
            - Use **bold** for important concepts
            - Use *italic* for emphasis
            - Use `code` for technical terms
            - Use ~~strikethrough~~ for deprecated concepts
            
            ### Blockquotes
            - Use > for important tips and warnings
            - Use for highlighting key insights
            
            ### Tables
            - Use proper table formatting for comparisons
            - Keep tables simple and readable
            
            ### Spacing
            - Add proper line breaks between sections
            - Use consistent spacing
            - Don't over-format - keep it clean
            
            ### Special Elements
            - Use callouts for important information
            - Use dividers (---) to separate major sections
            - Use emojis strategically for engagement
            
            Return the properly formatted MDX content that maintains all the original information while being much more readable and visually appealing.
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
        """Fix header formatting."""
        # Ensure proper header hierarchy
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.startswith('# '):
                # Convert H1 to H2 for better hierarchy
                line = line.replace('# ', '## ')
            elif line.startswith('## ') and 'Quick Answer' in line:
                # Keep Quick Answer as H2
                pass
            elif line.startswith('## ') and any(keyword in line for keyword in ['Introduction', 'Code Example', 'Why This Concept']):
                # Keep main sections as H2
                pass
            elif line.startswith('### ') and any(keyword in line for keyword in ['Memory Trick', 'Pro Tips', 'Career Impact']):
                # Keep subsections as H3
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
        """Fix list formatting."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix bullet points
            if line.strip().startswith('- ') and not line.strip().startswith('- **'):
                # Add emphasis to list items
                line = line.replace('- ', '- **')
                if not line.endswith('**'):
                    line = line + '**'
            
            # Fix numbered lists
            if re.match(r'^\d+\.\s', line.strip()):
                # Ensure proper spacing
                line = re.sub(r'^(\d+\.)\s*', r'\1 ', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_spacing(self, content: str) -> str:
        """Fix spacing and line breaks."""
        # Add proper spacing between sections
        content = re.sub(r'##\s+([^\n]+)\n([^\n])', r'## \1\n\n\2', content)
        content = re.sub(r'###\s+([^\n]+)\n([^\n])', r'### \1\n\n\2', content)
        
        # Add spacing around code blocks
        content = re.sub(r'\n```', r'\n\n```', content)
        content = re.sub(r'```\n', r'```\n\n', content)
        
        # Add spacing around lists
        content = re.sub(r'\n- ', r'\n\n- ', content)
        content = re.sub(r'\n[0-9]+\. ', r'\n\n\g<0>', content)
        
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