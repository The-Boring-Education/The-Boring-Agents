"""
Quiz generation commands.
"""
import click
import json
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def quiz_group():
    """Quiz generation commands."""
    pass


@quiz_group.command()
@click.option('--topic', required=True, help='Quiz topic (e.g., React, Python, DevOps)')
@click.option('--question-count', default=20, help='Number of questions to generate')
@click.option('--target-audience', default='developers', help='Target audience (beginners, developers, experts)')
@click.option('--save', is_flag=True, help='Save output to file')
def generate(topic, question_count, target_audience, save):
    """Generate a complete quiz for a technology topic."""
    console.print(f"[green]🎯 Generating {question_count} question quiz for {topic}...[/green]")
    
    try:
        # Import quiz orchestrator
        from src.agents.quiz import QuizOrchestrator
        
        # Create orchestrator
        orchestrator = QuizOrchestrator()
        
        # Generate quiz
        result = orchestrator.generate_complete_quiz(
            topic=topic,
            question_count=question_count,
            target_audience=target_audience
        )
        
        if result.get("status") == "success":
            console.print(f"[green]✅ Quiz generated successfully![/green]")
            console.print(f"[blue]📊 Quality Score: {result.get('quality_score', 'N/A')}/10[/blue]")
            
            if save:
                console.print(f"[blue]📁 Quiz saved to: {result.get('output_file', 'N/A')}[/blue]")
            else:
                # Display quiz summary
                quiz_data = result.get("quiz", {})
                console.print(f"\n[cyan]Quiz: {quiz_data.get('categoryName', topic)}[/cyan]")
                console.print(f"[cyan]Description: {quiz_data.get('categoryDescription', 'N/A')}[/cyan]")
                console.print(f"[cyan]Questions: {len(quiz_data.get('questions', []))}[/cyan]")
        else:
            console.print(f"[red]❌ Error generating quiz: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise click.Abort()


@quiz_group.command()
@click.option('--quiz-file', required=True, help='Path to quiz JSON file')
def validate(quiz_file):
    """Validate a quiz file for correctness and quality."""
    console.print(f"[blue]🔍 Validating quiz file: {quiz_file}[/blue]")
    
    try:
        # Import quiz uploader for validation
        from src.agents.quiz import QuizUploader
        
        # Load quiz data
        with open(quiz_file, 'r') as f:
            data = json.load(f)
        
        # Extract quiz data
        quiz_data = data.get("quiz", data)
        
        # Create uploader and validate
        uploader = QuizUploader()
        result = uploader.validate_quiz(quiz_data)
        
        if result.get("status") == "success":
            console.print(f"[green]✅ Quiz validation passed![/green]")
        else:
            console.print(f"[red]❌ Quiz validation failed![/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise click.Abort()


@quiz_group.command()
@click.option('--quiz-file', required=True, help='Path to quiz JSON file')
@click.option('--api-url', help='API URL (defaults to config)')
@click.option('--admin-secret', default='TBEAdmin', help='Admin secret for authentication')
def upload(quiz_file, api_url, admin_secret):
    """Upload a quiz to the database."""
    console.print(f"[green]🚀 Uploading quiz from: {quiz_file}[/green]")
    
    try:
        # Import quiz uploader
        from src.agents.quiz import QuizUploader
        
        # Create uploader
        uploader = QuizUploader(api_url=api_url, admin_secret=admin_secret)
        
        # Test connection first
        connection_result = uploader.test_connection()
        if connection_result.get("status") == "error":
            console.print(f"[red]❌ Cannot connect to API: {connection_result.get('message')}[/red]")
            return
        
        # Upload quiz
        result = uploader.upload_quiz_from_file(quiz_file)
        
        if result.get("status") == "success":
            console.print(f"[green]✅ Quiz uploaded successfully![/green]")
            console.print(f"[blue]📝 Quiz ID: {result.get('quiz_id', 'N/A')}[/blue]")
        else:
            console.print(f"[red]❌ Upload failed: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise click.Abort()


@quiz_group.command()
@click.option('--session-id', help='Session ID to resume')
def resume(session_id):
    """Resume a paused quiz generation session."""
    try:
        from src.agents.quiz import QuizOrchestrator
        
        orchestrator = QuizOrchestrator()
        
        if not session_id:
            # List available sessions
            sessions_result = orchestrator.list_active_sessions()
            sessions = sessions_result.get("sessions", [])
            
            if not sessions:
                console.print("[yellow]No active sessions found.[/yellow]")
                return
            
            # Display sessions
            table = Table(title="📋 Active Quiz Sessions")
            table.add_column("Session ID", style="cyan")
            table.add_column("Topic", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Questions", style="blue")
            table.add_column("Created", style="white")
            
            for session in sessions:
                table.add_row(
                    session.get("session_id", ""),
                    session.get("topic", ""),
                    session.get("status", ""),
                    str(session.get("questions_generated", 0)),
                    session.get("created_at", "")[:19]
                )
            
            console.print(table)
            
            # Ask user to select
            session_id = console.input("\n[yellow]Enter session ID to resume: [/yellow]")
        
        # Resume session
        result = orchestrator.resume_quiz_generation(session_id)
        
        if result.get("status") == "success":
            console.print(f"[green]✅ Session resumed and completed![/green]")
            console.print(f"[blue]📁 Output: {result.get('output_file', 'N/A')}[/blue]")
        else:
            console.print(f"[red]❌ Error: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        raise click.Abort()

