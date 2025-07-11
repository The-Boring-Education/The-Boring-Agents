"""
Main entry point for The Boring Agents CLI application.
"""

import sys
import os
import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import config
from src.agents import ContentAgent, InterviewAgent, ProjectAgent
from src.utils.helpers import setup_logging, generate_filename

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


@content.command()
@click.option('--topic', required=True, help='Course topic (e.g., "Node.js Backend Development")')
@click.option('--level', default='intermediate', type=click.Choice(['beginner', 'intermediate', 'advanced']), help='Difficulty level')
@click.option('--roadmap', default='Backend', help='Learning roadmap category')
@click.option('--description', help='Course description (auto-generated if not provided)')
@click.option('--save', is_flag=True, help='Save output to file')
def shiksha_course(topic, level, roadmap, description, save):
    """Generate a complete SHIKSHA course with chapters and content."""
    console.print(f"[green]Generating complete SHIKSHA course for {topic}...[/green]")
    
    agent = ContentAgent()
    result = agent.create_shiksha_course(topic, level, roadmap, description)
    
    # Display course summary
    course_data = result['generated_content']['data']
    
    table = Table(title=f"SHIKSHA Course: {course_data['name']}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Course Name", course_data['name'])
    table.add_row("Slug", course_data['slug'])
    table.add_row("Difficulty", course_data['difficultyLevel'])
    table.add_row("Roadmap", course_data['roadmap'])
    table.add_row("Chapters", str(len(course_data['chapters'])))
    table.add_row("Live Date", course_data['liveOn'][:10])
    
    console.print(table)
    console.print(f"\n[yellow]Description:[/yellow] {course_data['description']}")
    
    # Show chapter list
    chapters_table = Table(title="Course Chapters")
    chapters_table.add_column("#", style="cyan", width=3)
    chapters_table.add_column("Chapter Name", style="green")
    
    for i, chapter in enumerate(course_data['chapters'], 1):
        chapters_table.add_row(str(i), chapter['name'])
    
    console.print(chapters_table)
    
    if save:
        filename = generate_filename(f"shiksha_course_{topic.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@content.command()
@click.option('--chapter-name', required=True, help='Name of the chapter')
@click.option('--course-topic', required=True, help='Overall course topic')
@click.option('--description', required=True, help='Brief description of chapter content')
@click.option('--level', default='intermediate', help='Difficulty level')
@click.option('--save', is_flag=True, help='Save output to file')
def shiksha_chapter(chapter_name, course_topic, description, level, save):
    """Generate detailed content for a SHIKSHA course chapter."""
    console.print(f"[green]Generating chapter content for '{chapter_name}'...[/green]")
    
    agent = ContentAgent()
    result = agent.create_shiksha_chapter(chapter_name, course_topic, description, level)
    
    console.print(Panel(result['generated_content'], title=f"Chapter: {chapter_name}"))
    
    if save:
        filename = generate_filename(f"chapter_{chapter_name.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")


@content.command()
@click.option('--topic', required=True, help='Topic/technology learned')
@click.option('--achievement', required=True, help='What was accomplished')
@click.option('--learning-points', required=True, help='Key learning points (comma-separated)')
@click.option('--save', is_flag=True, help='Save output to file')
def social_media(topic, achievement, learning_points, save):
    """Generate social media sharing templates."""
    console.print(f"[green]Generating social media templates for {topic}...[/green]")
    
    learning_list = [point.strip() for point in learning_points.split(',')]
    
    agent = ContentAgent()
    result = agent.generate_social_media_templates(topic, achievement, learning_list)
    
    console.print(Panel(result['generated_content'], title=f"Social Media Templates: {topic}"))
    
    if save:
        filename = generate_filename(f"social_media_{topic.replace(' ', '_')}")
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