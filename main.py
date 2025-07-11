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
    ContentAgent, InterviewAgent, ProjectAgent, 
    ShikshaOrchestrator, EnhancedShikshaOrchestrator,
    InterviewSheetOrchestrator
)
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


@interview.command()
@click.option('--sheet-id', required=True, help='ID of the interview sheet to revamp')
@click.option('--save', is_flag=True, help='Save output to file')
def revamp_sheet(sheet_id, save):
    """Revamp an existing interview sheet with world-class quality."""
    console.print(f"[green]🚀 Revamping interview sheet: {sheet_id}...[/green]")
    
    try:
        orchestrator = InterviewSheetOrchestrator()
        result = orchestrator.revamp_existing_sheet(sheet_id)
        
        # Display results
        stats = result.get("statistics", {})
        table = Table(title=f"Revamping Results: {result.get('sheet_name', 'Unknown')}")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        
        table.add_row("Enhanced Questions", str(stats.get("enhanced", 0)))
        table.add_row("New Questions Added", str(stats.get("added", 0)))
        table.add_row("Failed Updates", str(stats.get("failed", 0)))
        
        console.print(table)
        
        # Show research insights
        insights = result.get("research_insights", {})
        if insights:
            console.print(f"\n📊 [bold]Key Research Insights:[/bold]")
            for rec in insights.get("key_recommendations", [])[:3]:
                console.print(f"   • {rec}")
        
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"revamped_sheet_{sheet_id}_{timestamp}"
            filepath = f"./output/{filename}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            console.print(f"[blue]Results saved to: {filepath}[/blue]")
        
        console.print(f"\n🎉 Sheet revamping completed successfully!")
        
    except Exception as e:
        console.print(f"[red]Error revamping sheet: {str(e)}[/red]")
        raise click.Abort()


@interview.command()
@click.option('--sheet-name', required=True, help='Name of the new interview sheet')
@click.option('--description', required=True, help='Description of the sheet topic')
@click.option('--target-questions', default=50, help='Number of questions to generate')
@click.option('--save', is_flag=True, help='Save output to file')
def create_world_class_sheet(sheet_name, description, target_questions, save):
    """Create a new world-class interview sheet from scratch."""
    console.print(f"[green]🚀 Creating world-class interview sheet: {sheet_name}...[/green]")
    
    try:
        orchestrator = InterviewSheetOrchestrator()
        result = orchestrator.create_new_sheet(sheet_name, description, target_questions)
        
        # Display results
        stats = result.get("statistics", {})
        sheet_data = result.get("sheet_data", {})
        
        table = Table(title=f"New Sheet Created: {sheet_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Questions", str(sheet_data.get("total_questions", 0)))
        table.add_row("Average Quality Score", f"{stats.get('average_quality_score', 0):.1f}/10")
        table.add_row("Estimated Prep Time", sheet_data.get("estimated_prep_time", "N/A"))
        
        console.print(table)
        
        # Show difficulty distribution
        difficulty_dist = sheet_data.get("difficulty_distribution", {})
        if difficulty_dist:
            console.print(f"\n📊 [bold]Difficulty Distribution:[/bold]")
            for difficulty, count in difficulty_dist.items():
                console.print(f"   {difficulty}: {count} questions")
        
        # Show metadata
        metadata = sheet_data.get("metadata", {})
        if metadata:
            console.print(f"\n✨ [bold]Quality Features:[/bold]")
            console.print(f"   🇮🇳 Indian Context: {metadata.get('indian_context', False)}")
            console.print(f"   😄 Humor Integrated: {metadata.get('humor_integrated', False)}")
            console.print(f"   ✅ Quality Assured: {metadata.get('quality_assured', False)}")
        
        if save:
            filepath = result.get("filepath", "")
            console.print(f"[blue]Sheet saved to: {filepath}[/blue]")
        
        console.print(f"\n🎉 World-class interview sheet created successfully!")
        console.print(f"[yellow]This sheet is ready for ₹49 premium pricing![/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error creating sheet: {str(e)}[/red]")
        raise click.Abort()


@interview.command()
@click.option('--save', is_flag=True, help='Save batch results to file')
def revamp_all_sheets(save):
    """Revamp ALL existing interview sheets in the database."""
    console.print(f"[green]🚀 Starting batch revamping of all interview sheets...[/green]")
    console.print(f"[yellow]⚠️  This will process ALL sheets in the database. Continue? [Y/n][/yellow]")
    
    import sys
    if not click.confirm(""):
        console.print("Operation cancelled.")
        return
    
    try:
        orchestrator = InterviewSheetOrchestrator()
        results = orchestrator.batch_revamp_all_sheets()
        
        # Display batch results
        table = Table(title="Batch Revamping Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        
        table.add_row("Total Sheets", str(results.get("total_sheets", 0)))
        table.add_row("Successfully Revamped", str(results.get("successful", 0)))
        table.add_row("Failed", str(results.get("failed", 0)))
        
        console.print(table)
        
        # Show individual results
        batch_results = results.get("results", [])
        if batch_results:
            console.print(f"\n📋 [bold]Individual Sheet Results:[/bold]")
            for result in batch_results[:10]:  # Show first 10
                status_emoji = "✅" if result["status"] == "success" else "❌"
                console.print(f"   {status_emoji} {result['sheet_name']}")
            
            if len(batch_results) > 10:
                console.print(f"   ... and {len(batch_results) - 10} more sheets")
        
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_revamp_results_{timestamp}"
            filepath = f"./output/{filename}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            console.print(f"[blue]Batch results saved to: {filepath}[/blue]")
        
        console.print(f"\n🎉 Batch revamping completed!")
        
    except Exception as e:
        console.print(f"[red]Error in batch revamping: {str(e)}[/red]")
        raise click.Abort()


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


@shiksha.command()
@click.option('--course-name', required=True, help='Name of the course')
@click.option('--description', required=True, help='Course description')
@click.option('--difficulty', default='Beginner', help='Difficulty level (Beginner, Intermediate, Advanced)')
@click.option('--roadmap', default='Backend', help='Roadmap category (Backend, Frontend, Full Stack, etc.)')
@click.option('--api-url', help='Custom API URL for research (optional)')
@click.option('--save', is_flag=True, help='Save output to file')
def create_world_class_course(course_name, description, difficulty, roadmap, api_url, save):
    """Create a world-class Shiksha course with Indian context, humor, and excellent instruction."""
    console.print(f"[green]🚀 Creating world-class Shiksha course: {course_name}...[/green]")
    
    try:
        orchestrator = EnhancedShikshaOrchestrator()
        course_data = orchestrator.create_world_class_course(
            course_name=course_name,
            description=description,
            difficulty_level=difficulty,
            roadmap=roadmap,
            api_base_url=api_url
        )
        
        # Display course summary
        data = course_data.get("data", {})
        chapters = data.get("chapters", [])
        
        table = Table(title=f"🌟 World-Class Shiksha Course: {course_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Course Name", data.get("name", "N/A"))
        table.add_row("Slug", data.get("slug", "N/A"))
        table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
        table.add_row("Roadmap", data.get("roadmap", "N/A"))
        table.add_row("Chapters", str(len(chapters)))
        table.add_row("Enhanced Features", ", ".join(data.get("features", [])))
        table.add_row("Live Date", data.get("liveOn", "N/A"))
        
        console.print(table)
        
        # Show research insights if available
        research_insights = course_data.get("research_insights", {})
        if research_insights:
            console.print("\n📊 [bold]Research Insights:[/bold]")
            for recommendation in research_insights.get("key_recommendations", [])[:3]:
                console.print(f"   • {recommendation}")
        
        if save:
            filepath = orchestrator.save_course(course_data)
            console.print(f"[blue]✅ World-class course saved to: {filepath}[/blue]")
        
        console.print(f"\n[yellow]🎉 World-class course creation completed successfully![/yellow]")
        console.print(f"[green]This course includes:[/green]")
        console.print("   🇮🇳 Indian context and examples")
        console.print("   😄 Humor and engaging analogies")
        console.print("   🛠️ Hands-on exercises and projects")
        console.print("   💼 Career-focused content")
        console.print("   📊 Research-based insights")
        
    except Exception as e:
        console.print(f"[red]❌ Error creating world-class course: {str(e)}[/red]")
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