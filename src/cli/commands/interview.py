"""
Interview preparation commands.
"""
import click
import json
import subprocess
import sys
from rich.console import Console
from rich.table import Table

from src.core.config import config
from src.agents.interview import InterviewSheetManager, DatabaseIntegrationAgent, AnswerAgentType

console = Console()


@click.group()
def interview_group():
    """Generate interview preparation content."""
    pass


@interview_group.command()
@click.option('--mdx-file', required=True, help='Path to MDX file containing interview requirements')
@click.option('--agent-type', type=click.Choice([e.value for e in AnswerAgentType]), default='generic', help='Type of answer creator agent to use')
@click.option('--technology', help='Technology focus for tech agent (e.g., Python, React, Java, DevOps)')
@click.option('--save', is_flag=True, help='Save output to file')
def generate_questions_from_mdx(mdx_file, agent_type, technology, save):
    """Step 1: Generate interview questions from MDX requirements file."""
    console.print(f"[green]🤖 Step 1: Generating questions from requirements using {agent_type} agent...[/green]")
    
    try:
        agent_enum = AnswerAgentType(agent_type)
        
        # Pass technology parameter for tech agents
        kwargs = {}
        if agent_type == 'tech' and technology:
            kwargs['technology'] = technology
            console.print(f"[blue]🔧 Technology focus: {technology}[/blue]")
        
        manager = InterviewSheetManager(agent_type=agent_enum, **kwargs)
        result = manager.generate_questions_from_mdx(mdx_file)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Questions generated successfully![/green]")
            console.print(f"[blue]📁 Questions file: {result['filepath']}[/blue]")
            console.print(f"[blue]📊 Questions generated: {result['questions_count']}[/blue]")
            
            console.print(f"\n[yellow]⚠️  Review the generated questions[/yellow]")
            console.print(f"[green]Then run: python main.py interview add-metadata-to-mdx --mdx-file {result['filepath']} --agent-type {agent_type}{' --technology ' + technology if technology else ''}[/green]")
            
        else:
            console.print(f"[red]❌ Error generating questions: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error generating questions: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--mdx-file', required=True, help='Path to MDX file containing interview requirements and context')
@click.option('--agent-type', type=click.Choice([e.value for e in AnswerAgentType]), default='generic', help='Type of answer creator agent to use')
@click.option('--technology', help='Technology focus for tech agent (e.g., Python, React, Java, DevOps)')
@click.option('--save', is_flag=True, help='Save output to file')
def create_sheet_from_mdx(mdx_file, agent_type, technology, save):
    """Step 1: Create interview sheet structure from MDX requirements."""
    console.print(f"[green]🤖 Step 1: Creating interview sheet from MDX using {agent_type} agent...[/green]")
    
    try:
        agent_enum = AnswerAgentType(agent_type)
        
        # Pass technology parameter for tech agents
        kwargs = {}
        if agent_type == 'tech' and technology:
            kwargs['technology'] = technology
            console.print(f"[blue]🔧 Technology focus: {technology}[/blue]")
        
        manager = InterviewSheetManager(agent_type=agent_enum, **kwargs)
        result = manager.create_sheet_from_mdx(mdx_file)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Sheet structure created successfully![/green]")
            console.print(f"[blue]📁 Sheet file: {result['filepath']}[/blue]")
            
            console.print(f"\n[yellow]⚠️  Review the sheet structure[/yellow]")
            console.print(f"[green]Then run: python main.py interview generate-questions-from-mdx --mdx-file {mdx_file}[/green]")
            
        else:
            console.print(f"[red]❌ Error creating sheet: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating sheet: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--mdx-file', required=True, help='Path to MDX file containing questions')
@click.option('--agent-type', type=click.Choice([e.value for e in AnswerAgentType]), default='generic', help='Type of answer creator agent to use')
@click.option('--technology', help='Technology focus for tech agent (e.g., Python, React, Java, DevOps)')
@click.option('--save', is_flag=True, help='Save output to file')
def add_metadata_to_mdx(mdx_file, agent_type, technology, save):
    """Step 2: Add metadata to questions in MDX file."""
    console.print(f"[green]🤖 Step 2: Adding metadata to questions in MDX using {agent_type} agent...[/green]")
    
    try:
        agent_enum = AnswerAgentType(agent_type)
        
        # Pass technology parameter for tech agents
        kwargs = {}
        if agent_type == 'tech' and technology:
            kwargs['technology'] = technology
            console.print(f"[blue]🔧 Technology focus: {technology}[/blue]")
        
        manager = InterviewSheetManager(agent_type=agent_enum, **kwargs)
        result = manager.add_metadata_to_mdx(mdx_file)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Metadata added successfully![/green]")
            console.print(f"[blue]📁 Enhanced MDX: {result['enhanced_filepath']}[/blue]")
            console.print(f"[blue]📊 Questions processed: {result['questions_count']}[/blue]")
            
            console.print(f"\n[yellow]⚠️  Review the enhanced MDX file[/yellow]")
            console.print(f"[green]Then run: python main.py interview generate-answers-from-mdx --mdx-file {result['enhanced_filepath']}[/green]")
            
        else:
            console.print(f"[red]❌ Error adding metadata: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error adding metadata: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--mdx-file', required=True, help='Path to MDX file containing questions')
@click.option('--agent-type', type=click.Choice([e.value for e in AnswerAgentType]), default='generic', help='Type of answer creator agent to use')
@click.option('--technology', help='Technology focus for tech agent (e.g., Python, React, Java, DevOps)')
@click.option('--save', is_flag=True, help='Save output to file')
def generate_answers_from_mdx(mdx_file, agent_type, technology, save):
    """Step 3: Generate answers for questions from MDX file."""
    console.print(f"[green]🤖 Step 3: Generating answers from MDX questions using {agent_type} agent...[/green]")
    
    try:
        agent_enum = AnswerAgentType(agent_type)
        
        # Pass technology parameter for tech agents
        kwargs = {}
        if agent_type == 'tech' and technology:
            kwargs['technology'] = technology
            console.print(f"[blue]🔧 Technology focus: {technology}[/blue]")
        
        manager = InterviewSheetManager(agent_type=agent_enum, **kwargs)
        result = manager.generate_answers_from_mdx(mdx_file)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Answers generated successfully![/green]")
            console.print(f"[blue]📁 Complete sheet: {result['filepath']}[/blue]")
            console.print(f"[blue]📊 Questions processed: {result['questions_count']}[/blue]")
            
            console.print(f"\n[yellow]🎯 Ready for database publication![/yellow]")
            console.print(f"[green]Run: python main.py interview publish-sheet --sheet-file {result['filepath']} --sheet-id your_sheet_id[/green]")
            
        else:
            console.print(f"[red]❌ Error generating answers: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error generating answers: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--agent-type', type=click.Choice([e.value for e in AnswerAgentType]), default='generic', help='Type of answer creator agent to use')
def list_sessions(agent_type):
    """List all active generation sessions."""
    console.print(f"[green]🔍 Listing active {agent_type} generation sessions...[/green]")
    
    try:
        agent_enum = AnswerAgentType(agent_type)
        manager = InterviewSheetManager(agent_type=agent_enum)
        result = manager.list_active_sessions()
        
        if result["status"] == "success":
            sessions = result["sessions"]
            
            if not sessions:
                console.print(f"[yellow]📋 No active sessions found[/yellow]")
                return
            
            # Filter sessions by agent type
            filtered_sessions = [s for s in sessions if s["agent_type"] == agent_type]
            
            if not filtered_sessions:
                console.print(f"[yellow]📋 No active {agent_type} sessions found[/yellow]")
                return
            
            # Display sessions in a table
            table = Table(title=f"Active {agent_type.title()} Generation Sessions")
            table.add_column("Topic", style="cyan")
            table.add_column("Progress", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Last Updated", style="blue")
            table.add_column("Session ID", style="dim")
            
            for session in filtered_sessions:
                table.add_row(
                    session["topic"],
                    session["progress"],
                    session["status"],
                    session["last_updated"][:19] if session["last_updated"] != "unknown" else "unknown",
                    session["session_id"][:8] + "..." if session["session_id"] != "unknown" else "unknown"
                )
            
            console.print(table)
            
            console.print(f"\n[yellow]💡 To resume a session:[/yellow]")
            console.print(f"[green]python main.py interview resume-session --session-id <session_id> --agent-type {agent_type}[/green]")
            
        else:
            console.print(f"[red]❌ Error listing sessions: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error listing sessions: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--session-id', help='Session ID to resume (if not provided, will show list)')
@click.option('--agent-type', type=click.Choice([e.value for e in AnswerAgentType]), default='generic', help='Type of answer creator agent to use')
def resume_session(session_id, agent_type):
    """Resume an interrupted generation session."""
    console.print(f"[green]🔄 Resuming {agent_type} generation session...[/green]")
    
    try:
        agent_enum = AnswerAgentType(agent_type)
        manager = InterviewSheetManager(agent_type=agent_enum)
        
        if not session_id:
            # Show available sessions and let user choose
            result = manager.list_active_sessions()
            if result["status"] == "success":
                sessions = [s for s in result["sessions"] if s["agent_type"] == agent_type]
                
                if not sessions:
                    console.print(f"[yellow]📋 No active {agent_type} sessions found[/yellow]")
                    return
                
                console.print(f"[yellow]📋 Available {agent_type} sessions:[/yellow]")
                for i, session in enumerate(sessions, 1):
                    console.print(f"{i}. {session['topic']} ({session['progress']}) - {session['session_id'][:8]}...")
                
                choice = click.prompt("Select session number", type=int)
                if 1 <= choice <= len(sessions):
                    selected_session = sessions[choice - 1]
                    session_filepath = selected_session["filepath"]
                else:
                    console.print(f"[red]❌ Invalid choice[/red]")
                    return
            else:
                console.print(f"[red]❌ Error listing sessions: {result.get('message', 'Unknown error')}[/red]")
                return
        else:
            # Find session by ID
            result = manager.list_active_sessions()
            if result["status"] == "success":
                sessions = result["sessions"]
                matching_session = None
                
                for session in sessions:
                    if session["session_id"].startswith(session_id) and session["agent_type"] == agent_type:
                        matching_session = session
                        break
                
                if not matching_session:
                    console.print(f"[red]❌ Session not found: {session_id}[/red]")
                    return
                
                session_filepath = matching_session["filepath"]
            else:
                console.print(f"[red]❌ Error finding session: {result.get('message', 'Unknown error')}[/red]")
                return
        
        # Resume the session
        result = manager.resume_session(session_filepath)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Session resumed and completed successfully![/green]")
            console.print(f"[blue]📁 Final sheet: {result['filepath']}[/blue]")
            console.print(f"[blue]📊 Questions processed: {result['questions_count']}[/blue]")
        else:
            console.print(f"[red]❌ Error resuming session: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error resuming session: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--json-file', required=True, help='Path to JSON file with generated answers')
@click.option('--output-file', help='Output file path (optional)')
def fix_mdx_formatting(json_file, output_file):
    """Fix MDX formatting issues in generated answers."""
    console.print(f"[green]🔧 Fixing MDX formatting in answers...[/green]")
    
    try:
        # Build command
        cmd = [sys.executable, "scripts/fix_mdx_formatting.py", json_file]
        if output_file:
            cmd.append(output_file)
        
        # Run the script
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[green]✅ MDX formatting fixed successfully![/green]")
            console.print(result.stdout)
        else:
            console.print(f"[red]❌ Error fixing MDX formatting:[/red]")
            console.print(result.stderr)
            
    except Exception as e:
        console.print(f"[red]❌ Error running fix script: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--json-file', required=True, help='Path to JSON file with questions to push')
@click.option('--sheet-id', required=True, help='Interview sheet ID in database')
@click.option('--api-url', default='http://localhost:3000', help='API base URL')
@click.option('--admin-secret', default='TBEAdmin', help='Admin secret for authentication')
def push_to_database(json_file, sheet_id, api_url, admin_secret):
    """Push questions to database using the new reliable script."""
    console.print(f"[green]🚀 Pushing questions to database...[/green]")
    
    try:
        # Build command
        cmd = [
            sys.executable, "scripts/push_to_database.py",
            json_file, sheet_id,
            "--api-url", api_url,
            "--admin-secret", admin_secret
        ]
        
        # Run the script interactively
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            console.print(f"[green]✅ Database push completed successfully![/green]")
        else:
            console.print(f"[red]❌ Database push failed or partially failed.[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error running database push script: {str(e)}[/red]")
        raise click.Abort()


@interview_group.command()
@click.option('--sheet-file', required=True, help='Path to final sheet JSON file to publish')
@click.option('--sheet-id', help='Interview sheet ID (if not provided, will prompt)')
@click.option('--agent-type', type=click.Choice([e.value for e in AnswerAgentType]), default='generic', help='Type of answer creator agent that was used')
@click.option('--save', is_flag=True, help='Save output to file')
def publish_sheet(sheet_file, sheet_id, agent_type, save):
    """Step 4: Publish sheet to database (DEPRECATED - use push-to-database instead)."""
    console.print(f"[yellow]⚠️  DEPRECATED: This command is deprecated. Use 'fix-mdx-formatting' then 'push-to-database' instead.[/yellow]")
    console.print(f"[blue]New workflow:[/blue]")
    console.print(f"  1. python3 main.py interview fix-mdx-formatting --json-file {sheet_file}")
    console.print(f"  2. python3 main.py interview push-to-database --json-file {sheet_file} --sheet-id YOUR_SHEET_ID")
    
    if not click.confirm("Continue with deprecated method?"):
        console.print(f"[yellow]Operation cancelled. Use the new workflow above.[/yellow]")
        return
    
    console.print(f"[green]🤖 Step 4: Publishing sheet to database (created with {agent_type} agent)...[/green]")
    
    try:
        # Load sheet data
        with open(sheet_file, 'r') as f:
            sheet_data = json.load(f)
        
        console.print(f"[green]✅ Sheet loaded successfully![/green]")
        console.print(f"[blue]📊 Sheet: {sheet_data.get('name', 'Unknown')}[/blue]")
        console.print(f"[blue]📊 Questions: {sheet_data.get('question_count', 0)}[/blue]")
        
        if not sheet_id:
            sheet_id = click.prompt("Enter sheet ID for database")
        
        console.print(f"[green]🎯 Ready to publish with ID: {sheet_id}[/green]")
        console.print(f"[yellow]⚠️  This will update the database. Continue?[/yellow]")
        
        if click.confirm("Proceed with publication?"):
            # Create an instance of DatabaseIntegrationAgent
            db_agent = DatabaseIntegrationAgent()
            
            # Validate sheet data first
            validation_result = db_agent.validate_sheet_data(sheet_data)
            if not validation_result.get("valid", False):
                console.print(f"[red]❌ Sheet validation failed: {validation_result.get('message', 'Unknown error')}[/red]")
                if validation_result.get("errors"):
                    for error in validation_result["errors"]:
                        console.print(f"[red]  - {error}[/red]")
                raise click.Abort()
            
            # Add questions to the existing sheet
            result = db_agent.add_questions_to_sheet(sheet_id, sheet_data.get("questions", []))
            
            if result["status"] == "success":
                console.print(f"[green]✅ Sheet published successfully![/green]")
                console.print(f"[blue]📊 Sheet ID: {sheet_id}[/blue]")
                console.print(f"[blue]📊 Questions added: {result.get('added_questions', 0)}[/blue]")
                console.print(f"[blue]📊 Total questions: {result.get('total_questions', 0)}[/blue]")
            else:
                console.print(f"[red]❌ Error publishing sheet: {result.get('message', 'Unknown error')}[/red]")
        else:
            console.print(f"[yellow]⚠️  Publication cancelled[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Error publishing sheet: {str(e)}[/red]")
        raise click.Abort()

