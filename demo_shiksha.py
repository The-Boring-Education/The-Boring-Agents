#!/usr/bin/env python3
"""
SHIKSHA Course Generation Demo
This script demonstrates the complete SHIKSHA course generation functionality.
"""

import sys
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.json import JSON

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents')
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents/src')

console = Console()

def demo_shiksha_course_generation():
    """Demonstrate SHIKSHA course generation."""
    console.print(Panel.fit(
        "[bold blue]SHIKSHA Course Generation Demo[/bold blue]\n"
        "Generating a complete backend development course",
        title="Demo"
    ))
    
    try:
        from src.agents.content_agent import ContentAgent
        
        # Mock the LLM to simulate course generation
        class MockLLM:
            def predict(self, prompt):
                if "shiksha_course" in prompt.lower():
                    return """
                    # Zero to One Backend Development with Node.js
                    
                    Complete backend development course covering Node.js fundamentals to advanced topics.
                    Perfect for beginners who want to become full-stack developers.
                    
                    ## Course Structure:
                    - GitHub and Version Control
                    - Node.js Fundamentals  
                    - Express.js Framework
                    - Database Integration
                    - Authentication & Security
                    - API Development
                    - Project Building
                    - Deployment Strategies
                    """
                elif "social_media" in prompt.lower():
                    return """
                    **LinkedIn Post:**
                    🚀 Just completed Backend Development with Node.js!
                    
                    Here's what I achieved:
                    1️⃣ Built complete REST APIs from scratch
                    2️⃣ Mastered Express.js framework and middleware
                    3️⃣ Implemented authentication and security
                    4️⃣ Deployed applications to production
                    
                    Backend development is the backbone of modern applications!
                    
                    🎓 Learning all this in Shiksha by The Boring Education. 🚀
                    
                    #NodeJS #Backend #ExpressJS #Shiksha #TheBoringEducation
                    
                    **Twitter Post:**
                    ✅ Completed Backend Development with Node.js!
                    
                    🔹 REST APIs ✔
                    🔹 Express.js ✔  
                    🔹 Authentication ✔
                    🔹 Production deployment ✔
                    
                    Loving this journey with Shiksha by The Boring Education! 💻
                    
                    #NodeJS #Backend #Shiksha #CodingJourney
                    """
                return "Mock content generated for demonstration"
        
        # Create agent and set up mock
        agent = ContentAgent()
        agent._llm = MockLLM()
        
        console.print("[green]Generating complete SHIKSHA course...[/green]")
        
        # Generate the course
        result = agent.create_shiksha_course(
            topic="Zero to One Backend Development with Node.js",
            level="beginner",
            roadmap="Backend",
            description="Start Your Backend Dev Journey. Projects Included."
        )
        
        course_data = result["generated_content"]["data"]
        
        # Display course overview
        table = Table(title="Generated SHIKSHA Course")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")
        
        table.add_row("Course Name", course_data["name"])
        table.add_row("Slug", course_data["slug"])
        table.add_row("Difficulty", course_data["difficultyLevel"])
        table.add_row("Roadmap", course_data["roadmap"])
        table.add_row("Chapters", str(len(course_data["chapters"])))
        table.add_row("Cover Image", course_data["coverImageURL"])
        table.add_row("Live Date", course_data["liveOn"][:10])
        
        console.print(table)
        console.print(f"\n[yellow]Description:[/yellow] {course_data['description']}")
        
        # Display chapters
        chapters_table = Table(title="Course Chapters")
        chapters_table.add_column("#", style="cyan", width=3)
        chapters_table.add_column("Chapter Name", style="green")
        chapters_table.add_column("Content Preview", style="yellow")
        
        for i, chapter in enumerate(course_data["chapters"], 1):
            preview = chapter["content"][:100] + "..." if len(chapter["content"]) > 100 else chapter["content"]
            chapters_table.add_row(str(i), chapter["name"], preview)
        
        console.print(chapters_table)
        
        # Show sample chapter content
        console.print("\n[bold]Sample Chapter Content (MDX Format):[/bold]")
        sample_chapter = course_data["chapters"][0]
        console.print(Panel(sample_chapter["content"][:500] + "...", title=f"Chapter: {sample_chapter['name']}"))
        
        # Generate social media templates
        console.print("\n[green]Generating social media templates...[/green]")
        social_result = agent.generate_social_media_templates(
            topic="Backend Development with Node.js",
            achievement="Completed full backend course",
            learning_points=["REST APIs", "Express.js", "Authentication", "Database integration"]
        )
        
        console.print(Panel(social_result["generated_content"], title="Social Media Templates"))
        
        # Save the course
        console.print("\n[green]Saving course to JSON file...[/green]")
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = os.path.join(output_dir, "demo_shiksha_course.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result["generated_content"], f, indent=2, ensure_ascii=False)
        
        console.print(f"[blue]Course saved to: {filename}[/blue]")
        
        # Display JSON structure
        console.print("\n[bold]Generated JSON Structure:[/bold]")
        # Show just the structure, not the full content
        structure = {
            "status": course_data.get("status", True),
            "data": {
                "_id": "course_id_example",
                "name": course_data["name"],
                "slug": course_data["slug"],
                "coverImageURL": course_data["coverImageURL"],
                "description": course_data["description"],
                "liveOn": course_data["liveOn"],
                "roadmap": course_data["roadmap"],
                "difficultyLevel": course_data["difficultyLevel"],
                "chapters": [
                    {
                        "name": "Sample Chapter",
                        "content": "# Chapter content in MDX format...",
                        "_id": "chapter_id_example",
                        "createdAt": "2025-01-29T09:01:09.636Z",
                        "updatedAt": "2025-01-29T09:01:09.636Z"
                    }
                ]
            }
        }
        
        console.print(JSON.from_data(structure))
        
        return True
        
    except Exception as e:
        console.print(f"[red]Demo failed: {e}[/red]")
        return False

def demo_cli_commands():
    """Demonstrate available CLI commands."""
    console.print("\n" + "="*60)
    console.print("[bold blue]Available CLI Commands:[/bold blue]")
    
    commands = [
        {
            "command": "python main.py content shiksha-course",
            "description": "Generate complete SHIKSHA course",
            "example": '--topic "React Development" --level beginner --roadmap Frontend --save'
        },
        {
            "command": "python main.py content shiksha-chapter", 
            "description": "Generate individual chapter content",
            "example": '--chapter-name "React Hooks" --course-topic "React Development" --description "Learn React Hooks" --save'
        },
        {
            "command": "python main.py content social-media",
            "description": "Generate social media templates",
            "example": '--topic "React" --achievement "Built first React app" --learning-points "Components,Hooks,State" --save'
        }
    ]
    
    for cmd in commands:
        console.print(f"\n[cyan]{cmd['command']}[/cyan]")
        console.print(f"  {cmd['description']}")
        console.print(f"  Example: [yellow]{cmd['example']}[/yellow]")

def main():
    """Run the demo."""
    try:
        # Run the main demo
        success = demo_shiksha_course_generation()
        
        if success:
            # Show CLI commands
            demo_cli_commands()
            
            console.print("\n" + "="*60)
            console.print("[bold green]Demo completed successfully![/bold green]")
            console.print("SHIKSHA course generation is ready for production use.")
            console.print("Check the generated course file in ./output/demo_shiksha_course.json")
        else:
            console.print("[red]Demo failed![/red]")
            return 1
            
    except Exception as e:
        console.print(f"[red]Demo error: {e}[/red]")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())