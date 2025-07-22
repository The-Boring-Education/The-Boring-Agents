#!/usr/bin/env python3
"""
Test script to send a single question to local environment and see what's being sent.
"""

import sys
import os
import json
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from src.core.config import config

console = Console()

def test_single_question():
    """Test sending a single question to local environment."""
    console.print(Panel.fit(
        "[bold blue]Single Question Test[/bold blue]\n"
        "Testing what gets sent to local environment",
        title="🧪 Single Question Test"
    ))
    
    # Test question data
    test_question = {
        "title": "What is the difference between list and tuple in Python?",
        "question": "What is the difference between list and tuple in Python?",
        "answer": "Lists and tuples are both sequence data types in Python, but they have key differences:\n\n1. **Mutability**: Lists are mutable (can be changed), tuples are immutable (cannot be changed)\n2. **Syntax**: Lists use square brackets [], tuples use parentheses ()\n3. **Performance**: Tuples are slightly faster and use less memory\n4. **Use cases**: Lists for dynamic data, tuples for fixed data\n\nExample:\n```python\nmy_list = [1, 2, 3]\nmy_tuple = (1, 2, 3)\n\nmy_list[0] = 10  # OK\nmy_tuple[0] = 10  # Error!\n```",
        "frequency": "Most Asked",
        "companyTypes": ["Startup", "MidSize", "MNC"]
    }
    
    console.print(f"\n[bold]Test Question Data:[/bold]")
    console.print(f"[blue]Environment: {config.environment}[/blue]")
    console.print(f"[blue]API Base URL: {config.api_base_url}[/blue]")
    console.print(f"[blue]API V1 URL: {config.api_v1_url}[/blue]")
    
    # Show what we're sending
    console.print(f"\n[bold]Payload being sent:[/bold]")
    payload_json = json.dumps(test_question, indent=2)
    syntax = Syntax(payload_json, "json", theme="monokai")
    console.print(syntax)
    
    # Test API call
    sheet_id = "67345538bdf619907a005031"  # Use the real sheet ID from your example
    api_url = f"{config.api_v1_url}/interview-prep/{sheet_id}/question"
    
    console.print(f"\n[bold]API Call Details:[/bold]")
    console.print(f"Method: POST")
    console.print(f"URL: {api_url}")
    console.print(f"Headers: x-admin-secret: TBEAdmin")
    console.print(f"Content-Type: application/json")
    
    try:
        # Make the API call
        console.print(f"\n[bold]Making API call...[/bold]")
        
        response = requests.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "x-admin-secret": "TBEAdmin"
            },
            json=test_question,
            timeout=10
        )
        
        console.print(f"\n[bold]Response:[/bold]")
        console.print(f"Status Code: {response.status_code}")
        console.print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            console.print(f"Response Body:")
            syntax = Syntax(json.dumps(response_json, indent=2), "json", theme="monokai")
            console.print(syntax)
        except:
            console.print(f"Response Text: {response.text}")
        
        if response.status_code in [200, 201]:
            console.print(f"\n[green]✅ Question sent successfully![/green]")
            # Check response body for success
            try:
                response_data = response.json()
                if response_data.get("status") == True:
                    console.print(f"[green]✅ API confirmed: {response_data.get('message', 'Success')}[/green]")
                else:
                    console.print(f"[yellow]⚠️  API returned: {response_data.get('message', 'Unknown')}[/yellow]")
            except:
                console.print(f"[green]✅ Question added with status code: {response.status_code}[/green]")
        else:
            console.print(f"\n[red]❌ Failed to send question[/red]")
            
    except requests.exceptions.ConnectionError:
        console.print(f"\n[red]❌ Connection failed - is localhost:3000 running?[/red]")
        console.print(f"[blue]Make sure your local API server is running on localhost:3000[/blue]")
        
    except requests.exceptions.Timeout:
        console.print(f"\n[red]❌ Request timeout[/red]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")

def test_question_structure():
    """Test the question structure in the final sheet."""
    console.print(f"\n[bold]Testing Question Structure in Final Sheet:[/bold]")
    
    # Look for final sheet
    output_dir = "./output"
    final_sheets = [f for f in os.listdir(output_dir) if f.startswith("final_sheet_") and f.endswith(".json")]
    
    if not final_sheets:
        console.print("[red]❌ No final sheet files found[/red]")
        return
    
    test_file = os.path.join(output_dir, final_sheets[0])
    console.print(f"[blue]Testing file: {test_file}[/blue]")
    
    try:
        with open(test_file, 'r') as f:
            sheet_data = json.load(f)
        
        # Check first question
        questions = sheet_data.get("questions", [])
        if questions:
            first_question = questions[0]
            
            console.print(f"\n[bold]First Question Structure:[/bold]")
            table = Table(title="Question Fields")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Present", style="yellow")
            
            # Check all possible fields
            all_fields = ['question', 'answer', 'difficulty', 'frequency', 'priority', 'category', 'companyTypes', 'roadmap']
            
            for field in all_fields:
                value = first_question.get(field, "NOT PRESENT")
                present = "✅" if field in first_question else "❌"
                table.add_row(field, str(value)[:50] + "..." if len(str(value)) > 50 else str(value), present)
            
            console.print(table)
            
            # Show what would be sent to API
            api_payload = {
                "title": first_question["question"],
                "question": first_question["question"],
                "answer": first_question["answer"],
                "frequency": first_question["frequency"],
                "companyTypes": first_question.get("companyTypes", ["Startup", "MidSize", "MNC"])
            }
            
            console.print(f"\n[bold]What gets sent to API:[/bold]")
            syntax = Syntax(json.dumps(api_payload, indent=2), "json", theme="monokai")
            console.print(syntax)
            
            # Check if companyTypes is missing
            if "companyTypes" not in first_question:
                console.print(f"\n[yellow]⚠️  companyTypes is NOT in the question data[/yellow]")
                console.print(f"[blue]This means it won't be sent to the API[/blue]")
            else:
                console.print(f"\n[green]✅ companyTypes is present in question data[/green]")
                
        else:
            console.print(f"[red]❌ No questions found in sheet[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error testing question structure: {str(e)}[/red]")

def main():
    """Run the single question test."""
    console.print(Panel.fit(
        "[bold green]Single Question API Test[/bold green]\n"
        "Testing what gets sent to local environment",
        title="🚀 Single Question Test Runner"
    ))
    
    # Test question structure first
    test_question_structure()
    
    # Test API call
    test_single_question()
    
    console.print(f"\n[bold green]✅ Single question test completed![/bold green]")

if __name__ == "__main__":
    main() 