"""
Main entry point for The Boring Agents CLI application.
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.core.config import config
from src.agents import ContentAgent, InterviewAgent, ProjectAgent, ShikshaOrchestrator
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
    """Generate content for Shiksha tech courses."""
    pass


@content.command()
@click.option('--topic', required=True, help='Course topic')
@click.option('--level', default='intermediate', help='Difficulty level')
@click.option('--duration', default='4 weeks', help='Course duration')
@click.option('--save', is_flag=True, help='Save output to file')
def course_outline(topic, level, duration, save):
    """Generate a course outline."""
    console.print(f"[green]Generating course outline for {topic}...[/green]")
    
    agent = ContentAgent()
    result = agent.create_course_outline(topic, level, duration)
    
    # Display result
    console.print(Panel(result['generated_content'], title=f"Course Outline: {topic}"))
    
    if save:
        filename = generate_filename(f"course_outline_{topic.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@content.command()
@click.option('--topic', required=True, help='Course topic')
@click.option('--module', required=True, help='Module title')
@click.option('--save', is_flag=True, help='Save output to file')
def video_suggestions(topic, module, save):
    """Generate video suggestions for a module."""
    console.print(f"[green]Generating video suggestions for {module}...[/green]")
    
    agent = ContentAgent()
    result = agent.suggest_videos(topic, module)
    
    console.print(Panel(result['generated_content'], title=f"Video Suggestions: {module}"))
    
    if save:
        filename = generate_filename(f"videos_{module.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@content.command()
@click.option('--topic', required=True, help='Technology topic')
@click.option('--level', default='intermediate', help='Experience level')
@click.option('--save', is_flag=True, help='Save output to file')
def tips_and_tricks(topic, level, save):
    """Generate tips and tricks for a technology."""
    console.print(f"[green]Generating tips and tricks for {topic}...[/green]")
    
    agent = ContentAgent()
    result = agent.generate_tricks_and_tips(topic, level)
    
    console.print(Panel(result['generated_content'], title=f"Tips & Tricks: {topic}"))
    
    if save:
        filename = generate_filename(f"tips_{topic.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@cli.group()
def interview():
    """Generate interview preparation content."""
    pass


@interview.command()
@click.option('--technology', required=True, help='Technology/framework')
@click.option('--level', default='intermediate', help='Experience level')
@click.option('--count', default=25, help='Number of questions')
@click.option('--save', is_flag=True, help='Save output to file')
def question_sheet(technology, level, count, save):
    """Generate interview question sheet."""
    console.print(f"[green]Generating {count} interview questions for {technology}...[/green]")
    
    agent = InterviewAgent()
    result = agent.create_question_sheet(technology, level, count)
    
    console.print(Panel(result['generated_content'], title=f"{technology} Interview Questions"))
    
    if save:
        filename = generate_filename(f"interview_{technology.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@interview.command()
@click.option('--technology', required=True, help='Programming language/technology')
@click.option('--difficulty', default='medium', help='Challenge difficulty')
@click.option('--count', default=10, help='Number of challenges')
@click.option('--save', is_flag=True, help='Save output to file')
def coding_challenges(technology, difficulty, count, save):
    """Generate coding challenges."""
    console.print(f"[green]Generating {count} coding challenges for {technology}...[/green]")
    
    agent = InterviewAgent()
    result = agent.create_coding_challenges(technology, difficulty, count)
    
    console.print(Panel(result['generated_content'], title=f"{technology} Coding Challenges"))
    
    if save:
        filename = generate_filename(f"coding_{technology.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@interview.command()
@click.option('--technology', required=True, help='Primary technology')
@click.option('--level', default='intermediate', help='Experience level')
@click.option('--save', is_flag=True, help='Save output to file')
def complete_prep(technology, level, save):
    """Generate complete interview preparation package."""
    console.print(f"[green]Generating complete interview prep for {technology}...[/green]")
    
    agent = InterviewAgent()
    result = agent.create_complete_interview_prep(technology, level)
    
    # Display summary
    table = Table(title=f"Interview Prep Package: {technology}")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    for component in result['components'].keys():
        table.add_row(component.replace('_', ' ').title(), "✓ Generated")
    
    console.print(table)
    console.print(f"[yellow]Estimated prep time: {result['metadata']['total_prep_time']}[/yellow]")
    
    if save:
        filename = generate_filename(f"complete_prep_{technology.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@cli.group()
def projects():
    """Generate project ideas and implementations."""
    pass


@cli.group()
def shiksha():
    """Generate complete Shiksha courses."""
    pass


@shiksha.command()
@click.option('--course-name', required=True, help='Name of the course')
@click.option('--description', required=True, help='Course description')
@click.option('--difficulty', default='Beginner', help='Difficulty level (Beginner, Intermediate, Advanced)')
@click.option('--roadmap', default='Backend', help='Roadmap category (Backend, Frontend, Full Stack, etc.)')
@click.option('--save', is_flag=True, help='Save output to file')
def create_course(course_name, description, difficulty, roadmap, save):
    """Create a complete Shiksha course with all components."""
    console.print(f"[green]Creating complete Shiksha course: {course_name}...[/green]")
    
    try:
        orchestrator = ShikshaOrchestrator()
        course_data = orchestrator.create_complete_course(
            course_name=course_name,
            description=description,
            difficulty_level=difficulty,
            roadmap=roadmap
        )
        
        # Display course summary
        data = course_data.get("data", {})
        chapters = data.get("chapters", [])
        
        table = Table(title=f"Shiksha Course: {course_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Course Name", data.get("name", "N/A"))
        table.add_row("Slug", data.get("slug", "N/A"))
        table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
        table.add_row("Roadmap", data.get("roadmap", "N/A"))
        table.add_row("Chapters", str(len(chapters)))
        table.add_row("Live Date", data.get("liveOn", "N/A"))
        
        console.print(table)
        
        if save:
            filepath = orchestrator.save_course(course_data)
            console.print(f"[blue]Course saved to: {filepath}[/blue]")
        
        console.print(f"[yellow]Course creation completed successfully![/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error creating course: {str(e)}[/red]")
        raise click.Abort()


@projects.command()
@click.option('--technology', required=True, help='Primary technology')
@click.option('--domain', default='web development', help='Project domain')
@click.option('--difficulty', default='intermediate', help='Project difficulty')
@click.option('--count', default=5, help='Number of projects')
@click.option('--save', is_flag=True, help='Save output to file')
def ideas(technology, domain, difficulty, count, save):
    """Generate project ideas."""
    console.print(f"[green]Generating {count} project ideas using {technology}...[/green]")
    
    agent = ProjectAgent()
    result = agent.generate_project_ideas(technology, difficulty, count, domain)
    
    console.print(Panel(result['generated_content'], title=f"{technology} Project Ideas"))
    
    if save:
        filename = generate_filename(f"projects_{technology.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@projects.command()
@click.option('--project', required=True, help='Project name')
@click.option('--technologies', required=True, help='Technology stack')
@click.option('--save', is_flag=True, help='Save output to file')
def architecture(project, technologies, save):
    """Generate project architecture."""
    console.print(f"[green]Generating architecture for {project}...[/green]")
    
    agent = ProjectAgent()
    result = agent.create_project_architecture(project, technologies)
    
    console.print(Panel(result['generated_content'], title=f"Architecture: {project}"))
    
    if save:
        filename = generate_filename(f"architecture_{project.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@projects.command()
@click.option('--technology', required=True, help='Primary technology')
@click.option('--domain', default='web development', help='Project domain')
@click.option('--difficulty', default='intermediate', help='Project difficulty')
@click.option('--save', is_flag=True, help='Save output to file')
def complete_package(technology, domain, difficulty, save):
    """Generate complete project package."""
    console.print(f"[green]Generating complete project package for {technology}...[/green]")
    
    agent = ProjectAgent()
    result = agent.create_complete_project_package(technology, domain, difficulty)
    
    # Display summary
    if 'components' in result:
        table = Table(title=f"Project Package: {technology}")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        
        for component in result['components'].keys():
            table.add_row(component.replace('_', ' ').title(), "✓ Generated")
        
        console.print(table)
        console.print(f"[yellow]Estimated completion time: {result['metadata']['estimated_completion_time']}[/yellow]")
    else:
        console.print(Panel(result['generated_content'], title=f"{technology} Projects"))
    
    if save:
        filename = generate_filename(f"project_package_{technology.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@cli.command()
def status():
    """Show configuration status."""
    table = Table(title="Configuration Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")
    
    table.add_row("OpenAI API Key", "***" if config.openai_api_key else "Not set", 
                  "✓" if config.openai_api_key else "✗")
    table.add_row("Default Model", config.default_model, "✓")
    table.add_row("Output Directory", config.output_dir, "✓")
    table.add_row("Log Level", config.log_level, "✓")
    
    console.print(table)


if __name__ == '__main__':
    cli()