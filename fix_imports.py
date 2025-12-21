"""Fix all langchain imports to use langchain_core"""
import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace imports
    content = re.sub(r'from langchain\.prompts import', 'from langchain_core.prompts import', content)
    content = re.sub(r'from langchain\.schema import BaseOutputParser', 'from langchain_core.output_parsers import BaseOutputParser', content)
    content = re.sub(r'from langchain\.llms\.base import LLM', 'from langchain_core.language_models.chat_models import BaseChatModel', content)
    
    # Replace type hints
    content = re.sub(r'-> LLM:', '-> BaseChatModel:', content)
    content = re.sub(r'def llm\(self\) -> LLM:', 'def llm(self) -> BaseChatModel:', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    src_dir = r'N:\Work_space\The-Boring-Agents\src'
    fixed_count = 0
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    print(f"Fixed: {filepath}")
                    fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
