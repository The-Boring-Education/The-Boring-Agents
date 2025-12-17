"""
Content generation commands.
"""
import click
import json
import os
from rich.console import Console
from rich.table import Table

from src.core.config import config
from src.agents import ContentAgent
from src.utils import generate_filename

console = Console()


@click.group()
def content_group():
    """Generate educational content."""
    pass


@content_group.command()
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


@content_group.command()
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


@content_group.command()
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

