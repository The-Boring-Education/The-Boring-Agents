#!/usr/bin/env python3
"""
Fix MDX Formatting Script

This script fixes the MDX formatting issues in generated interview answer JSON files.
It removes the ```mdx\n prefix and \n``` suffix from all answers to ensure proper UI display.

Usage:
    python scripts/fix_mdx_formatting.py <input_file> [output_file]

Example:
    python scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json
    python scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json output/fixed_sheet.json
"""

import json
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, TaskID

console = Console()


def fix_answer_formatting(answer: str) -> str:
    """
    Remove MDX code block formatting from answer content.
    
    Args:
        answer (str): The original answer with MDX formatting
        
    Returns:
        str: The cleaned answer without MDX formatting
    """
    # Remove leading ```mdx\n if present
    if answer.startswith('```mdx\n'):
        answer = answer[7:]  # Remove '```mdx\n'
    
    # Remove trailing \n``` if present
    if answer.endswith('\n```'):
        answer = answer[:-4]  # Remove '\n```'
    elif answer.endswith('```'):
        answer = answer[:-3]  # Remove '```'
    
    # Clean up any remaining leading/trailing whitespace
    return answer.strip()


def fix_json_file(input_file: str, output_file: str = None) -> bool:
    """
    Fix MDX formatting in a JSON file containing interview questions.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to the output JSON file (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Determine output file path
        if output_file is None:
            # Create backup and overwrite original
            backup_file = f"{input_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(input_file, backup_file)
            output_file = input_file
            console.print(f"[yellow]📁 Created backup: {backup_file}[/yellow]")
        
        # Load the JSON file
        console.print(f"[blue]📖 Loading file: {input_file if output_file == input_file else backup_file}[/blue]")
        with open(backup_file if output_file == input_file else input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate file structure
        if not isinstance(data, dict) or 'questions' not in data:
            console.print(f"[red]❌ Invalid file format. Expected JSON with 'questions' array.[/red]")
            return False
        
        questions = data.get('questions', [])
        total_questions = len(questions)
        
        if total_questions == 0:
            console.print(f"[yellow]⚠️  No questions found in the file.[/yellow]")
            return False
        
        console.print(f"[green]📊 Found {total_questions} questions to process[/green]")
        
        # Process questions with progress bar
        fixed_count = 0
        with Progress() as progress:
            task = progress.add_task("[cyan]Fixing MDX formatting...", total=total_questions)
            
            for i, question in enumerate(questions):
                if 'answer' in question and question['answer']:
                    original_answer = question['answer']
                    fixed_answer = fix_answer_formatting(original_answer)
                    
                    if original_answer != fixed_answer:
                        question['answer'] = fixed_answer
                        fixed_count += 1
                
                progress.update(task, advance=1)
        
        # Save the fixed file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Summary
        console.print(f"[green]✅ Processing complete![/green]")
        console.print(f"[blue]📊 Total questions: {total_questions}[/blue]")
        console.print(f"[blue]🔧 Answers fixed: {fixed_count}[/blue]")
        console.print(f"[blue]📁 Output file: {output_file}[/blue]")
        
        if fixed_count > 0:
            console.print(f"[green]🎉 Successfully fixed MDX formatting in {fixed_count} answers![/green]")
        else:
            console.print(f"[yellow]ℹ️  No MDX formatting issues found.[/yellow]")
        
        return True
        
    except FileNotFoundError:
        console.print(f"[red]❌ File not found: {input_file}[/red]")
        return False
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Invalid JSON format: {str(e)}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error processing file: {str(e)}[/red]")
        return False


def main():
    """Main function to handle command line arguments and execute the fix."""
    if len(sys.argv) < 2:
        console.print("[red]❌ Usage: python scripts/fix_mdx_formatting.py <input_file> [output_file][/red]")
        console.print("[yellow]Examples:[/yellow]")
        console.print("  python scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json")
        console.print("  python scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json output/fixed_sheet.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate input file exists
    if not os.path.exists(input_file):
        console.print(f"[red]❌ Input file does not exist: {input_file}[/red]")
        sys.exit(1)
    
    console.print("🔧 [bold]MDX Formatting Fix Tool[/bold]")
    console.print("=" * 50)
    
    success = fix_json_file(input_file, output_file)
    
    if success:
        console.print(f"\n[green]🎉 MDX formatting fixed successfully![/green]")
        sys.exit(0)
    else:
        console.print(f"\n[red]❌ Failed to fix MDX formatting.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 