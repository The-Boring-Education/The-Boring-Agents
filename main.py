"""
Main entry point for The Boring Agents CLI application.
"""

import click
import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.core.config import config
from src.agents import (
    ContentAgent, ProjectAgent, 
    ShikshaOrchestrator, EnhancedShikshaOrchestrator
)
from src.agents.project import ProjectOrchestratorAgent
from src.agents.interview import InterviewSheetManager, DatabaseIntegrationAgent, AnswerAgentType
from src.utils import setup_logging, generate_filename

console = Console()


@click.group()
@click.option('--log-level', default='INFO', help='Set logging level')
def cli(log_level):
    """The Boring Agents - AI-powered content generation for education."""
    setup_logging(log_level)
    
    # Validate configuration
    if not config.validate_api_keys():
        console.print("[red]Error: No API keys configured. Please set up your .env file.[/red]")
        console.print("Copy .env.example to .env and add your API keys.")
        raise click.Abort()
    
    console.print(Panel.fit(
        "[bold blue]The Boring Agents[/bold blue]\n"
        "AI-powered content generation for The Boring Education",
        title="Welcome"
    ))


@cli.group()
def content():
    """Generate educational content."""
    pass


@content.command()
@click.option('--topic', required=True, help='Course topic')
@click.option('--level', default='intermediate', help='Difficulty level')
@click.option('--duration', default='4 weeks', help='Course duration')
@click.option('--save', is_flag=True, help='Save output to file')
def course_outline(topic, level, duration, save):
    """Generate a course outline."""
    console.print(f"[green]🎯 Generating course outline for {topic}...[/green]")
    
    try:
        agent = ContentAgent()
        result = agent.create_course_outline(topic, level, duration)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Course outline generated successfully![/green]")
            
            if save:
                filename = generate_filename("course_outline", "json")
                filepath = os.path.join(config.output_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(result["data"], f, indent=2)
                console.print(f"[blue]📁 Saved to: {filepath}[/blue]")
            
            # Display summary
            data = result["data"]
            table = Table(title=f"📋 Course Outline: {topic}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Duration", data.get("duration", "N/A"))
            table.add_row("Level", data.get("level", "N/A"))
            table.add_row("Modules", str(len(data.get("modules", []))))
            table.add_row("Total Hours", str(data.get("total_hours", "N/A")))
            
            console.print(table)
            
        else:
            console.print(f"[red]❌ Error generating course outline: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error generating course outline: {str(e)}[/red]")
        raise click.Abort()


@content.command()
@click.option('--topic', required=True, help='Course topic')
@click.option('--module', required=True, help='Module title')
@click.option('--save', is_flag=True, help='Save output to file')
def video_suggestions(topic, module, save):
    """Generate video suggestions for a module."""
    console.print(f"[green]🎯 Generating video suggestions for {module}...[/green]")
    
    try:
        agent = ContentAgent()
        result = agent.suggest_videos(topic, module)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Video suggestions generated successfully![/green]")
            
            if save:
                filename = generate_filename("video_suggestions", "json")
                filepath = os.path.join(config.output_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(result["data"], f, indent=2)
                console.print(f"[blue]📁 Saved to: {filepath}[/blue]")
            
            # Display summary
            data = result["data"]
            console.print(f"\n📺 [bold]Video Suggestions for {module}:[/bold]")
            for i, video in enumerate(data.get("videos", []), 1):
                console.print(f"{i}. {video.get('title', 'N/A')} ({video.get('duration', 'N/A')})")
            
        else:
            console.print(f"[red]❌ Error generating video suggestions: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error generating video suggestions: {str(e)}[/red]")
        raise click.Abort()


@content.command()
@click.option('--topic', required=True, help='Technology topic')
@click.option('--level', default='intermediate', help='Experience level')
@click.option('--save', is_flag=True, help='Save output to file')
def tips_and_tricks(topic, level, save):
    """Generate tips and tricks for a technology."""
    console.print(f"[green]🎯 Generating tips and tricks for {topic}...[/green]")
    
    try:
        agent = ContentAgent()
        result = agent.generate_tricks_and_tips(topic, level)
        
        if result["status"] == "success":
            console.print(f"[green]✅ Tips and tricks generated successfully![/green]")
            
            if save:
                filename = generate_filename("tips_and_tricks", "json")
                filepath = os.path.join(config.output_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(result["data"], f, indent=2)
                console.print(f"[blue]📁 Saved to: {filepath}[/blue]")
            
            # Display summary
            data = result["data"]
            console.print(f"\n💡 [bold]Tips and Tricks for {topic}:[/bold]")
            for i, tip in enumerate(data.get("tips", []), 1):
                console.print(f"{i}. {tip.get('title', 'N/A')}")
            
        else:
            console.print(f"[red]❌ Error generating tips and tricks: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error generating tips and tricks: {str(e)}[/red]")
        raise click.Abort()


@cli.group()
def interview():
    """Generate interview preparation content."""
    pass


@interview.command()
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


@interview.command()
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


@interview.command()
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


@interview.command()
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


@interview.command()
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
            from rich.table import Table
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


@interview.command()
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


@interview.command()
@click.option('--json-file', required=True, help='Path to JSON file with generated answers')
@click.option('--output-file', help='Output file path (optional)')
def fix_mdx_formatting(json_file, output_file):
    """Fix MDX formatting issues in generated answers."""
    console.print(f"[green]🔧 Fixing MDX formatting in answers...[/green]")
    
    try:
        import subprocess
        import sys
        
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


@interview.command()
@click.option('--json-file', required=True, help='Path to JSON file with questions to push')
@click.option('--sheet-id', required=True, help='Interview sheet ID in database')
@click.option('--api-url', default='http://localhost:3000', help='API base URL')
@click.option('--admin-secret', default='TBEAdmin', help='Admin secret for authentication')
def push_to_database(json_file, sheet_id, api_url, admin_secret):
    """Push questions to database using the new reliable script."""
    console.print(f"[green]🚀 Pushing questions to database...[/green]")
    
    try:
        import subprocess
        import sys
        
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


@interview.command()
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


@cli.group()
def projects():
    """Generate project ideas and implementations."""
    pass


@projects.command()
@click.option('--idea', required=True, help='Project idea (can be a title or concept)')
@click.option('--description', required=True, help='Detailed description of what to build')
@click.option('--save', is_flag=True, help='Save output to JSON file')
def create(idea, description, save):
    """Create a complete project from just an idea and description (AI determines everything else)."""
    console.print(f"[green]🚀 Creating project from idea: {idea[:50]}...[/green]")
    
    try:
        orchestrator = ProjectOrchestratorAgent()
        project_data = orchestrator.create_complete_project(
            idea=idea,
            description=description
        )
        
        # Display project summary
        if project_data.get("status"):
            data = project_data.get("data", {})
            
            table = Table(title=f"🌟 Project Created: {data.get('name', 'Unknown')}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Project Name", data.get("name", "N/A"))
            table.add_row("Description", data.get("description", "N/A")[:100] + "...")
            table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
            table.add_row("Roadmap", data.get("roadmap", "N/A"))
            table.add_row("Sections", str(len(data.get("sections", []))))
            table.add_row("Required Skills", ", ".join(data.get("requiredSkills", [])[:3]) + "...")
            
            console.print(table)
            
            # Show career enhancement info
            career_enhancement = data.get("career_enhancement", {})
            if career_enhancement:
                console.print(f"\n💼 [bold]AI Determined Career Impact:[/bold]")
                console.print(f"   Target Role: {career_enhancement.get('target_role', 'N/A')}")
                console.print(f"   Salary Impact: {career_enhancement.get('salary_impact', 'N/A')}")
                console.print(f"   Skills Gained: {', '.join(career_enhancement.get('skills_gained', [])[:5])}")
            
            if save:
                filename = generate_filename("project", "json")
                filepath = os.path.join(config.output_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(project_data, f, indent=2)
                console.print(f"\n[blue]📁 Project saved to: {filepath}[/blue]")
            
        else:
            console.print(f"[red]❌ Error creating project: {project_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating project: {str(e)}[/red]")
        raise click.Abort()


@projects.command()
@click.option('--mdx-file', required=True, help='Path to MDX file containing project idea and description')
@click.option('--save', is_flag=True, help='Save output to JSON file')
def create_from_mdx(mdx_file, save):
    """Create a complete project from MDX file."""
    console.print(f"[green]🚀 Creating project from MDX: {mdx_file}[/green]")
    
    try:
        # Read MDX file
        with open(mdx_file, 'r', encoding='utf-8') as f:
            mdx_content = f.read()
        
        # Extract idea and description from MDX
        lines = mdx_content.split('\n')
        idea = ""
        description = ""
        
        for line in lines:
            if line.startswith('# ') and not idea:
                idea = line.replace('# ', '').strip()
            elif line.startswith('## ') and not description:
                description = line.replace('## ', '').strip()
            elif line and not description and not line.startswith('#'):
                description = line.strip()
                break
        
        if not idea:
            idea = "Project from MDX"
        if not description:
            description = "Project created from MDX requirements"
        
        # Create project
        orchestrator = ProjectOrchestratorAgent()
        project_data = orchestrator.create_complete_project(
            idea=idea,
            description=description
        )
        
        if project_data.get("status"):
            data = project_data.get("data", {})
            
            table = Table(title=f"🌟 Project Created: {data.get('name', 'Unknown')}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Project Name", data.get("name", "N/A"))
            table.add_row("Description", data.get("description", "N/A")[:100] + "...")
            table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
            table.add_row("Roadmap", data.get("roadmap", "N/A"))
            table.add_row("Sections", str(len(data.get("sections", []))))
            
            console.print(table)
            
            if save:
                filename = generate_filename("project_mdx", "json")
                filepath = os.path.join(config.output_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(project_data, f, indent=2)
                console.print(f"\n[blue]📁 Project saved to: {filepath}[/blue]")
            
        else:
            console.print(f"[red]❌ Error creating project: {project_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating project: {str(e)}[/red]")
        raise click.Abort()


@cli.group()
def shiksha():
    """Generate Shiksha course content."""
    pass


@shiksha.command()
@click.option('--course-name', required=True, help='Name of the course')
@click.option('--description', required=True, help='Course description')
@click.option('--difficulty', default='Beginner', help='Difficulty level (Beginner, Intermediate, Advanced)')
@click.option('--roadmap', default='Backend', help='Roadmap category (Backend, Frontend, Full Stack, etc.)')
@click.option('--save', is_flag=True, help='Save output to file')
def create_course(course_name, description, difficulty, roadmap, save):
    """Create a complete Shiksha course."""
    console.print(f"[green]🎓 Creating Shiksha course: {course_name}[/green]")
    
    try:
        orchestrator = ShikshaOrchestrator()
        result = orchestrator.create_complete_course(
            course_name=course_name,
            description=description,
            difficulty_level=difficulty,
            roadmap=roadmap
        )
        
        if result["status"] == "success":
            console.print(f"[green]✅ Course created successfully![/green]")
            
            data = result.get("data", {})
            table = Table(title=f"📚 Course: {data.get('name', 'Unknown')}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Course Name", data.get("name", "N/A"))
            table.add_row("Description", data.get("description", "N/A")[:100] + "...")
            table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
            table.add_row("Roadmap", data.get("roadmap", "N/A"))
            table.add_row("Chapters", str(len(data.get("chapters", []))))
            
            console.print(table)
            
            if save:
                filename = generate_filename("shiksha_course", "json")
                filepath = os.path.join(config.output_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(result, f, indent=2)
                console.print(f"\n[blue]📁 Course saved to: {filepath}[/blue]")
            
        else:
            console.print(f"[red]❌ Error creating course: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating course: {str(e)}[/red]")
        raise click.Abort()


@shiksha.command()
@click.option('--course-name', required=True, help='Name of the course')
@click.option('--description', required=True, help='Course description')
@click.option('--difficulty', default='Beginner', help='Difficulty level (Beginner, Intermediate, Advanced)')
@click.option('--roadmap', default='Backend', help='Roadmap category (Backend, Frontend, Full Stack, etc.)')
@click.option('--api-url', help='Custom API URL for research (optional)')
@click.option('--save', is_flag=True, help='Save output to file')
def create_world_class_course(course_name, description, difficulty, roadmap, api_url, save):
    """Create a world-class Shiksha course with enhanced research."""
    console.print(f"[green]🎓 Creating world-class course: {course_name}[/green]")
    
    try:
        orchestrator = EnhancedShikshaOrchestrator()
        result = orchestrator.create_world_class_course(
            course_name=course_name,
            description=description,
            difficulty_level=difficulty,
            roadmap=roadmap,
            api_base_url=api_url
        )
        
        if result["status"] == "success":
            console.print(f"[green]✅ World-class course created successfully![/green]")
            
            data = result.get("data", {})
            table = Table(title=f"🌟 World-Class Course: {data.get('name', 'Unknown')}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Course Name", data.get("name", "N/A"))
            table.add_row("Description", data.get("description", "N/A")[:100] + "...")
            table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
            table.add_row("Roadmap", data.get("roadmap", "N/A"))
            table.add_row("Chapters", str(len(data.get("chapters", []))))
            
            console.print(table)
            
            if save:
                filename = generate_filename("world_class_course", "json")
                filepath = os.path.join(config.output_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(result, f, indent=2)
                console.print(f"\n[blue]📁 Course saved to: {filepath}[/blue]")
            
        else:
            console.print(f"[red]❌ Error creating world-class course: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating world-class course: {str(e)}[/red]")
        raise click.Abort()


@cli.group()
def quiz():
    """Quiz generation commands."""
    pass


@quiz.command()
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


@quiz.command()
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


@quiz.command()
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


@quiz.command()
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


@cli.command()
def status():
    """Check system status and configuration."""
    console.print(f"[green]🔍 Checking system status...[/green]")
    
    # Check configuration
    table = Table(title="⚙️ System Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Environment", config.environment)
    table.add_row("API Base URL", config.api_base_url)
    table.add_row("Default Model", config.default_model)
    table.add_row("Max Tokens", str(config.max_tokens))
    table.add_row("Temperature", str(config.temperature))
    table.add_row("Output Directory", config.output_dir)
    
    console.print(table)
    
    # Check API keys
    api_keys_table = Table(title="🔑 API Keys Status")
    api_keys_table.add_column("Service", style="cyan")
    api_keys_table.add_column("Status", style="green")
    
    api_keys_table.add_row("OpenAI", "✅ Configured" if config.openai_api_key else "❌ Missing")
    api_keys_table.add_row("Anthropic", "✅ Configured" if config.anthropic_api_key else "❌ Missing")
    api_keys_table.add_row("HuggingFace", "✅ Configured" if config.huggingface_api_key else "❌ Missing")
    
    console.print(api_keys_table)
    
    # Check output directory
    if os.path.exists(config.output_dir):
        console.print(f"[green]✅ Output directory exists: {config.output_dir}[/green]")
    else:
        console.print(f"[yellow]⚠️  Output directory missing: {config.output_dir}[/yellow]")
        os.makedirs(config.output_dir, exist_ok=True)
        console.print(f"[green]✅ Created output directory[/green]")
    
    console.print(f"\n[green]🎉 System is ready![/green]")


if __name__ == "__main__":
    cli()