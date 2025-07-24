#!/usr/bin/env python3
"""
Database Push Script

This script pushes interview questions from a JSON file to the database using the API.
It loops through all questions, makes HTTP POST requests, and logs the progress.

Usage:
    python scripts/push_to_database.py <json_file> <sheet_id> [options]

Example:
    python scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031
    python scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031 --api-url http://localhost:3000 --admin-secret TBEAdmin
"""

import json
import sys
import os
import time
import argparse
import requests
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table
from rich.panel import Panel

console = Console()


class DatabasePusher:
    """
    A class to handle pushing interview questions to the database.
    """
    
    def __init__(self, api_url: str, admin_secret: str):
        """
        Initialize the database pusher.
        
        Args:
            api_url (str): Base API URL (e.g., http://localhost:3000)
            admin_secret (str): Admin secret for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.admin_secret = admin_secret
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'x-admin-secret': self.admin_secret,
            'Content-Type': 'application/json'
        })
    
    def validate_question_data(self, question: dict) -> tuple:
        """
        Validate and prepare question data for API.
        
        Args:
            question (dict): Question data from JSON
            
        Returns:
            tuple: (is_valid, formatted_data, error_message)
        """
        required_fields = ['question', 'answer', 'difficulty', 'frequency', 'priority', 'company_types']
        
        for field in required_fields:
            if field not in question:
                return False, None, f"Missing required field: {field}"
        
        # Prepare data in the format expected by the API
        api_data = {
            "title": question.get('title', question['question'])[:100],  # Limit title to 100 chars
            "question": question['question'],
            "answer": question['answer'],
            "difficulty": question['difficulty'],
            "frequency": question['frequency'],
            "priority": question['priority'],
            "companyTypes": question['company_types']
        }
        
        return True, api_data, None
    
    def push_single_question(self, sheet_id: str, question_data: dict) -> tuple:
        """
        Push a single question to the database.
        
        Args:
            sheet_id (str): The interview sheet ID
            question_data (dict): The question data to push
            
        Returns:
            tuple: (success, response_data, error_message)
        """
        url = f"{self.api_url}/api/v1/interview-prep/{sheet_id}/question"
        
        try:
            response = self.session.post(url, json=question_data, timeout=30)
            
            if response.status_code == 200 or response.status_code == 201:
                return True, response.json(), None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            return False, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection error - check if API server is running"
        except requests.exceptions.RequestException as e:
            return False, None, f"Request error: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def push_questions_from_file(self, json_file: str, sheet_id: str) -> dict:
        """
        Push all questions from a JSON file to the database.
        
        Args:
            json_file (str): Path to the JSON file containing questions
            sheet_id (str): The interview sheet ID
            
        Returns:
            dict: Results summary
        """
        results = {
            'total_questions': 0,
            'successful_pushes': 0,
            'failed_pushes': 0,
            'errors': [],
            'start_time': datetime.now(),
            'end_time': None
        }
        
        try:
            # Load the JSON file
            console.print(f"[blue]📖 Loading file: {json_file}[/blue]")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate file structure
            if not isinstance(data, dict) or 'questions' not in data:
                console.print(f"[red]❌ Invalid file format. Expected JSON with 'questions' array.[/red]")
                return results
            
            questions = data.get('questions', [])
            results['total_questions'] = len(questions)
            
            if results['total_questions'] == 0:
                console.print(f"[yellow]⚠️  No questions found in the file.[/yellow]")
                return results
            
            console.print(f"[green]📊 Found {results['total_questions']} questions to push[/green]")
            console.print(f"[blue]🎯 Target Sheet ID: {sheet_id}[/blue]")
            console.print(f"[blue]🌐 API URL: {self.api_url}[/blue]")
            
            # Process questions with progress bar
            with Progress() as progress:
                task = progress.add_task("[cyan]Pushing questions to database...", total=results['total_questions'])
                
                for i, question in enumerate(questions):
                    # Validate question data
                    is_valid, api_data, error_msg = self.validate_question_data(question)
                    
                    if not is_valid:
                        results['failed_pushes'] += 1
                        error_info = {
                            'question_index': i,
                            'question_title': question.get('question', 'Unknown')[:50],
                            'error': f"Validation error: {error_msg}"
                        }
                        results['errors'].append(error_info)
                        progress.update(task, advance=1)
                        continue
                    
                    # Push to database
                    success, response_data, error_msg = self.push_single_question(sheet_id, api_data)
                    
                    if success:
                        results['successful_pushes'] += 1
                        # Optional: Log successful pushes for debugging
                        # console.print(f"[green]✅ Pushed: {api_data['title'][:50]}[/green]")
                    else:
                        results['failed_pushes'] += 1
                        error_info = {
                            'question_index': i,
                            'question_title': question.get('question', 'Unknown')[:50],
                            'error': error_msg
                        }
                        results['errors'].append(error_info)
                    
                    progress.update(task, advance=1)
                    
                    # Small delay to avoid overwhelming the server
                    time.sleep(0.1)
            
            results['end_time'] = datetime.now()
            return results
            
        except FileNotFoundError:
            console.print(f"[red]❌ File not found: {json_file}[/red]")
            return results
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Invalid JSON format: {str(e)}[/red]")
            return results
        except Exception as e:
            console.print(f"[red]❌ Error processing file: {str(e)}[/red]")
            return results


def display_results_summary(results: dict):
    """
    Display a comprehensive summary of the push results.
    
    Args:
        results (dict): Results from the database push operation
    """
    # Calculate duration
    duration = "Unknown"
    if results['start_time'] and results['end_time']:
        duration_seconds = (results['end_time'] - results['start_time']).total_seconds()
        duration = f"{duration_seconds:.2f} seconds"
    
    # Create summary table
    table = Table(title="📊 Database Push Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Questions", str(results['total_questions']))
    table.add_row("Successfully Pushed", str(results['successful_pushes']))
    table.add_row("Failed to Push", str(results['failed_pushes']))
    table.add_row("Success Rate", f"{(results['successful_pushes'] / max(results['total_questions'], 1)) * 100:.1f}%")
    table.add_row("Duration", duration)
    
    console.print(table)
    
    # Display errors if any
    if results['errors']:
        console.print(f"\n[red]❌ Errors ({len(results['errors'])}):[/red]")
        for i, error in enumerate(results['errors'][:10], 1):  # Show first 10 errors
            console.print(f"  {i}. [yellow]{error['question_title']}[/yellow]: {error['error']}")
        
        if len(results['errors']) > 10:
            console.print(f"  ... and {len(results['errors']) - 10} more errors")


def main():
    """Main function to handle command line arguments and execute the database push."""
    parser = argparse.ArgumentParser(
        description="Push interview questions from JSON file to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031
  python scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031 --api-url http://localhost:3000
  python scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031 --admin-secret CustomSecret
        """
    )
    
    parser.add_argument('json_file', help='Path to the JSON file containing questions')
    parser.add_argument('sheet_id', help='Interview sheet ID in the database')
    parser.add_argument('--api-url', default='http://localhost:3000', 
                       help='API base URL (default: http://localhost:3000)')
    parser.add_argument('--admin-secret', default='TBEAdmin',
                       help='Admin secret for authentication (default: TBEAdmin)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate data without actually pushing to database')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.json_file):
        console.print(f"[red]❌ Input file does not exist: {args.json_file}[/red]")
        sys.exit(1)
    
    # Display header
    console.print(Panel.fit(
        "[bold blue]Database Push Tool[/bold blue]\n"
        "Push interview questions to database via API",
        title="🚀 TBE Interview Prep"
    ))
    
    # Initialize pusher
    pusher = DatabasePusher(args.api_url, args.admin_secret)
    
    if args.dry_run:
        console.print("[yellow]🧪 DRY RUN MODE - No data will be pushed to database[/yellow]")
        # TODO: Implement dry run validation
        console.print("[blue]Dry run mode not implemented yet[/blue]")
        return
    
    # Confirm before proceeding
    console.print(f"[yellow]⚠️  About to push questions to database:[/yellow]")
    console.print(f"  📁 File: {args.json_file}")
    console.print(f"  🎯 Sheet ID: {args.sheet_id}")
    console.print(f"  🌐 API URL: {args.api_url}")
    
    if not console.input("\n[bold]Continue? (y/N): [/bold]").lower().startswith('y'):
        console.print("[yellow]Operation cancelled.[/yellow]")
        sys.exit(0)
    
    # Execute the push
    console.print(f"\n[green]🚀 Starting database push...[/green]")
    results = pusher.push_questions_from_file(args.json_file, args.sheet_id)
    
    # Display results
    console.print(f"\n")
    display_results_summary(results)
    
    # Exit with appropriate code
    if results['failed_pushes'] == 0:
        console.print(f"\n[green]🎉 All questions pushed successfully![/green]")
        sys.exit(0)
    elif results['successful_pushes'] > 0:
        console.print(f"\n[yellow]⚠️  Partial success - some questions failed to push.[/yellow]")
        sys.exit(1)
    else:
        console.print(f"\n[red]❌ Failed to push any questions.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 