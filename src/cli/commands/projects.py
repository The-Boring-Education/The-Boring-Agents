"""
Project generation commands.
"""
import click
import json
import os
from rich.console import Console
from rich.table import Table

from src.core.config import config
from src.agents.project import ProjectOrchestratorAgent
from src.utils import generate_filename

console = Console()


@click.group()
def projects_group():
    """Generate project ideas and implementations."""
    pass


@projects_group.command()
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


@projects_group.command()
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

