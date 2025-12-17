"""
Shiksha course generation commands.
"""
import click
import json
import os
from rich.console import Console
from rich.table import Table

from src.core.config import config
from src.agents import ShikshaOrchestrator, EnhancedShikshaOrchestrator
from src.utils import generate_filename

console = Console()


@click.group()
def shiksha_group():
    """Generate Shiksha course content."""
    pass


@shiksha_group.command()
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


@shiksha_group.command()
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

