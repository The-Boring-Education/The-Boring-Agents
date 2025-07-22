#!/usr/bin/env python3
"""
Test script for the new Interview Sheet Creator functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.agents.interview.interview_sheet_creator import InterviewSheetCreator
from src.core.config import config

console = Console()

def test_interview_sheet_creator():
    """Test the interview sheet creator functionality."""
    console.print(Panel.fit(
        "[bold blue]Interview Sheet Creator Test[/bold blue]\n"
        "Testing the new phased interview sheet creation process",
        title="🧪 Test Suite"
    ))
    
    try:
        # Initialize the creator
        creator = InterviewSheetCreator()
        console.print("[green]✅ InterviewSheetCreator initialized successfully[/green]")
        
        # Test Phase 1: Create sheet
        console.print("\n[bold]Phase 1: Creating Interview Sheet[/bold]")
        result = creator.create_interview_sheet("Python", "Backend")
        
        if result["status"] == "success":
            console.print("[green]✅ Phase 1 completed successfully[/green]")
            
            # Display sheet info
            sheet_data = result["sheet_data"]
            table = Table(title="Created Sheet Info")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Name", sheet_data["name"])
            table.add_row("Slug", sheet_data["slug"])
            table.add_row("Roadmap", sheet_data["roadmap"])
            table.add_row("Questions Count", str(len(sheet_data["questions"])))
            table.add_row("File Path", result["filepath"])
            
            console.print(table)
            
            # Test Phase 2: Generate questions
            console.print("\n[bold]Phase 2: Generating Questions[/bold]")
            questions_result = creator.generate_questions_list("Python", "Backend", 5)
            
            if questions_result["status"] == "success":
                console.print("[green]✅ Phase 2 completed successfully[/green]")
                console.print(f"[blue]Questions saved to: {questions_result['mdx_filepath']}[/blue]")
                
                # Test Phase 3: Generate answers
                console.print("\n[bold]Phase 3: Generating Answers[/bold]")
                answers_result = creator.generate_answers_for_questions(
                    questions_result['mdx_filepath'],
                    result['filepath']
                )
                
                if answers_result["status"] == "success":
                    console.print("[green]✅ Phase 3 completed successfully[/green]")
                    console.print(f"[blue]Complete sheet saved to: {answers_result['filepath']}[/blue]")
                    
                    # Test Phase 4: Validate sheet
                    console.print("\n[bold]Phase 4: Validating Sheet[/bold]")
                    validation_result = creator.validate_sheet_for_publication(
                        answers_result['filepath']
                    )
                    
                    if validation_result["status"] == "success":
                        console.print("[green]✅ Phase 4 completed successfully[/green]")
                        console.print(f"[blue]Final sheet ready: {validation_result['filepath']}[/blue]")
                        
                        # Test Phase 5: Publish (mock)
                        console.print("\n[bold]Phase 5: Publishing to Database[/bold]")
                        publish_result = creator.publish_to_database(
                            validation_result['filepath']
                        )
                        
                        if publish_result["status"] == "success":
                            console.print("[green]✅ Phase 5 completed successfully[/green]")
                            console.print(f"[blue]Sheet ID: {publish_result['sheet_id']}[/blue]")
                            console.print(f"[blue]API URL: {publish_result['api_url']}[/blue]")
                        else:
                            console.print(f"[red]❌ Phase 5 failed: {publish_result.get('message')}[/red]")
                    else:
                        console.print(f"[red]❌ Phase 4 failed: {validation_result.get('message')}[/red]")
                else:
                    console.print(f"[red]❌ Phase 3 failed: {answers_result.get('message')}[/red]")
            else:
                console.print(f"[red]❌ Phase 2 failed: {questions_result.get('message')}[/red]")
        else:
            console.print(f"[red]❌ Phase 1 failed: {result.get('message')}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Test failed with error: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())

def test_configuration():
    """Test the configuration settings."""
    console.print("\n[bold]Configuration Test[/bold]")
    
    table = Table(title="Configuration Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")
    
    # Test API keys
    has_api_key = config.validate_api_keys()
    table.add_row("API Keys", "Configured" if has_api_key else "Missing", 
                  "✓" if has_api_key else "✗")
    
    # Test environment
    table.add_row("Environment", config.environment, "✓")
    table.add_row("API Base URL", config.api_base_url, "✓")
    table.add_row("Output Directory", config.output_dir, "✓")
    
    console.print(table)
    
    if not has_api_key:
        console.print("[yellow]⚠️  Warning: No API keys configured. Set OPENAI_API_KEY in .env file[/yellow]")

def main():
    """Run the test suite."""
    console.print(Panel.fit(
        "[bold green]Interview Sheet Creator Test Suite[/bold green]\n"
        "Testing the new phased interview sheet creation process",
        title="🚀 Test Runner"
    ))
    
    # Test configuration
    test_configuration()
    
    # Test functionality
    test_interview_sheet_creator()
    
    console.print("\n[bold green]✅ Test suite completed![/bold green]")

if __name__ == "__main__":
    main() 