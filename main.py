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
from src.agents.project import ProjectOrchestratorAgent
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


@projects.command()
@click.option('--domain', required=True, help='Domain/industry (fintech, edtech, healthtech, etc.)')
@click.option('--user-profile', default='College student looking for internships', help='Target user profile')
@click.option('--target-role', default='Software Developer', help='Target job role')
@click.option('--save', is_flag=True, help='Save output to JSON file')
def create_real_project(domain, user_profile, target_role, save):
    """Create a complete real-life project that boosts careers."""
    console.print(f"[green]🚀 Creating real-life project for {domain} domain...[/green]")
    
    try:
        orchestrator = ProjectOrchestratorAgent()
        project_data = orchestrator.create_complete_project(
            domain=domain,
            user_profile=user_profile,
            target_role=target_role
        )
        
        # Display project summary
        if project_data.get("status"):
            data = project_data.get("data", {})
            
            table = Table(title=f"🌟 Project Created: {data.get('name', 'Unknown')}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Project Name", data.get("name", "N/A"))
            table.add_row("Description", data.get("description", "N/A"))
            table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
            table.add_row("Roadmap", data.get("roadmap", "N/A"))
            table.add_row("Sections", str(len(data.get("sections", []))))
            table.add_row("Required Skills", ", ".join(data.get("requiredSkills", [])))
            
            console.print(table)
            
            # Show career enhancement info
            career_enhancement = data.get("career_enhancement", {})
            if career_enhancement:
                console.print(f"\n💼 [bold]Career Impact:[/bold]")
                console.print(f"   Target Role: {career_enhancement.get('target_role', 'N/A')}")
                console.print(f"   Skill Development: {len(career_enhancement.get('skill_development', []))} skills")
                console.print(f"   Salary Impact: {career_enhancement.get('salary_impact', {}).get('with_project', 'N/A')}")
            
            if save:
                filepath = orchestrator.save_project(project_data)
                console.print(f"[blue]✅ Project saved to: {filepath}[/blue]")
            
            console.print(f"\n[yellow]🎉 Real-life project created successfully![/yellow]")
            console.print(f"[green]This project will help you:[/green]")
            console.print("   📈 Stand out in the job market")
            console.print("   💰 Potentially increase salary by 20-50%")
            console.print("   🏢 Get interviews at top Indian companies")
            console.print("   🎯 Build a portfolio that impresses recruiters")
            
        else:
            console.print(f"[red]❌ Error creating project: {project_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating project: {str(e)}[/red]")
        raise click.Abort()


@projects.command()
@click.option('--project-idea', required=True, help='Custom project idea description')
@click.option('--user-profile', default='Indian developers', help='User profile for difficulty determination')
@click.option('--save', is_flag=True, help='Save output to JSON file')
def create_custom_project(project_idea, user_profile, save):
    """Create a project from your custom idea."""
    console.print(f"[green]🎯 Creating custom project: {project_idea[:50]}...[/green]")
    
    try:
        orchestrator = ProjectOrchestratorAgent()
        project_data = orchestrator.generate_project_from_idea(
            project_idea=project_idea,
            user_profile=user_profile
        )
        
        # Display project summary
        if project_data.get("status"):
            data = project_data.get("data", {})
            
            table = Table(title=f"🎨 Custom Project: {data.get('name', 'Unknown')}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Project Name", data.get("name", "N/A"))
            table.add_row("Description", data.get("description", "N/A"))
            table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
            table.add_row("Roadmap", data.get("roadmap", "N/A"))
            table.add_row("Sections", str(len(data.get("sections", []))))
            
            console.print(table)
            
            if save:
                filepath = orchestrator.save_project(project_data)
                console.print(f"[blue]✅ Custom project saved to: {filepath}[/blue]")
            
            console.print(f"\n[yellow]🎉 Custom project created successfully![/yellow]")
            
        else:
            console.print(f"[red]❌ Error creating custom project: {project_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating custom project: {str(e)}[/red]")
        raise click.Abort()


@projects.command() 
@click.option('--save', is_flag=True, help='Save output to JSON file')
def demo_fintech_project(save):
    """Create a demo fintech project (PaySplit Pro)."""
    console.print(f"[green]🚀 Creating demo fintech project: PaySplit Pro...[/green]")
    
    try:
        orchestrator = ProjectOrchestratorAgent()
        project_data = orchestrator.create_complete_project(
            domain="fintech",
            user_profile="College student looking for fintech internships",
            target_role="Full Stack Developer"
        )
        
        # Display results
        if project_data.get("status"):
            data = project_data.get("data", {})
            console.print(f"[green]✅ Demo project created: {data.get('name', 'PaySplit Pro')}[/green]")
            console.print(f"📊 Sections: {len(data.get('sections', []))}")
            console.print(f"🛠️ Skills: {', '.join(data.get('requiredSkills', []))}")
            
            if save:
                filepath = orchestrator.save_project(project_data)
                console.print(f"[blue]💾 Demo project saved to: {filepath}[/blue]")
        
        console.print(f"\n[yellow]🎉 Demo fintech project ready![/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Error creating demo project: {str(e)}[/red]")
        raise click.Abort()


@projects.command() 
@click.option('--save', is_flag=True, help='Save output to JSON file')
def demo_static_project(save):
    """Create a demo project with static data (no API required)."""
    console.print(f"[green]🚀 Creating demo project with static data...[/green]")
    
    try:
        from datetime import datetime
        import uuid
        
        # Create sample project data in the exact API schema format
        project_data = {
            "status": True,
            "message": "Project fetched successfully", 
            "data": {
                "_id": str(uuid.uuid4()).replace("-", "")[:24],
                "name": "PaySplit Pro - UPI Bill Splitting App",
                "description": "Build a modern bill-splitting app with UPI integration that solves real payment problems for Indian friend groups and families.",
                "coverImageURL": "https://ik.imagekit.io/tbe/webapp/tbp-paysplit-pro-1.svg",
                "slug": "paysplit-pro-upi-bill-splitting",
                "requiredSkills": ["React", "Node.js", "MongoDB", "Express.js", "UPI API"],
                "roadmap": "Full Stack",
                "difficultyLevel": "Intermediate", 
                "isActive": True,
                "sections": [
                    {
                        "sectionId": str(uuid.uuid4()).replace("-", "")[:24],
                        "sectionName": "1. Project Introduction & Setup",
                        "chapters": [
                            {
                                "chapterId": str(uuid.uuid4()).replace("-", "")[:24],
                                "chapterName": "1. Understanding the PaySplit Problem",
                                "content": "# 1. Understanding the PaySplit Problem\n\nWe've all been there - you're out with friends at a restaurant, someone pays the bill, and then begins the awkward dance of \"Who owes what?\" \n\n## The Real Problem in India\n\nIn India, group payments are everywhere:\n- College friends going out for dinner\n- Office colleagues ordering lunch\n- Family trips and expenses  \n- Roommates splitting utility bills\n- Wedding expense management\n\nCurrent solutions like Splitwise work but lack UPI integration, making actual payments a separate hassle.\n\n## Our Solution: PaySplit Pro\n\nWe're building an app that not only splits bills but also facilitates instant UPI payments, making the entire process seamless for Indian users.\n\n**What makes this special:**\n- Native UPI integration\n- Indian rupee calculations\n- Multiple split options (equal, percentage, custom)\n- Group expense tracking\n- Instant payment settlement\n\nThis project will teach you real-world skills that Indian fintech companies value highly.",
                                "isOptional": False
                            },
                            {
                                "chapterId": str(uuid.uuid4()).replace("-", "")[:24],
                                "chapterName": "2. Setting Up the Development Environment",
                                "content": "# 2. Setting Up the Development Environment\n\n## Prerequisites\n\nBefore we start building PaySplit Pro, make sure you have:\n\n1. **Node.js** (v16 or higher)\n2. **MongoDB** (local installation or MongoDB Atlas)\n3. **Git** for version control\n4. **VS Code** (recommended)\n5. **UPI Test Environment** (we'll use test APIs)\n\n## Project Structure\n\n```\npaysplit-pro/\n├── client/          # React frontend\n├── server/          # Node.js backend\n├── shared/          # Shared utilities\n└── docs/           # Documentation\n```\n\n## Initial Setup Commands\n\n```bash\n# Create project directory\nmkdir paysplit-pro\ncd paysplit-pro\n\n# Initialize backend\nmkdir server && cd server\nnpm init -y\nnpm install express mongoose cors dotenv\nnpm install -D nodemon\n\n# Initialize frontend\ncd ../\nnpx create-react-app client\ncd client\nnpm install axios react-router-dom styled-components\n```\n\n## Environment Variables\n\nCreate `.env` files for both frontend and backend with necessary configurations.\n\nNext up: We'll design the database schema for our bill-splitting app!",
                                "isOptional": False
                            }
                        ]
                    },
                    {
                        "sectionId": str(uuid.uuid4()).replace("-", "")[:24], 
                        "sectionName": "2. Database Design & Backend Architecture",
                        "chapters": [
                            {
                                "chapterId": str(uuid.uuid4()).replace("-", "")[:24],
                                "chapterName": "1. Designing the Database Schema",
                                "content": "# 1. Designing the Database Schema\n\n## Core Entities\n\nOur PaySplit Pro app needs these main collections:\n\n### Users Collection\n```javascript\n{\n  _id: ObjectId,\n  name: String,\n  email: String,\n  phone: String,\n  upiId: String,\n  avatar: String,\n  friends: [ObjectId], // references to other users\n  groups: [ObjectId],  // references to groups\n  createdAt: Date\n}\n```\n\n### Groups Collection\n```javascript\n{\n  _id: ObjectId,\n  name: String,\n  description: String,\n  members: [{\n    userId: ObjectId,\n    role: String, // 'admin' or 'member'\n    joinedAt: Date\n  }],\n  expenses: [ObjectId], // references to expenses\n  totalExpenses: Number,\n  createdBy: ObjectId,\n  createdAt: Date\n}\n```\n\n### Expenses Collection\n```javascript\n{\n  _id: ObjectId,\n  title: String,\n  amount: Number,\n  paidBy: ObjectId, // user who paid\n  groupId: ObjectId,\n  splits: [{\n    userId: ObjectId,\n    amount: Number,\n    settled: Boolean,\n    settledAt: Date\n  }],\n  category: String,\n  receipt: String, // image URL\n  date: Date,\n  createdAt: Date\n}\n```\n\n## Why This Schema Works\n\n1. **Scalable**: Can handle thousands of users and groups\n2. **Flexible**: Supports different split types\n3. **Indian Context**: UPI integration ready\n4. **Performance**: Optimized for common queries\n\nNext: We'll implement these schemas with Mongoose!",
                                "isOptional": False
                            }
                        ]
                    },
                    {
                        "sectionId": str(uuid.uuid4()).replace("-", "")[:24],
                        "sectionName": "3. Frontend Development with React",
                        "chapters": [
                            {
                                "chapterId": str(uuid.uuid4()).replace("-", "")[:24],
                                "chapterName": "1. Building the User Interface",
                                "content": "# 1. Building the User Interface\n\n## Design Principles for Indian Users\n\nOur PaySplit Pro UI follows these principles:\n\n1. **Mobile-first**: Most Indians use mobile apps\n2. **Simple navigation**: Easy for all age groups\n3. **Rupee-centric**: All amounts in ₹\n4. **UPI-focused**: Prominent payment options\n5. **Group-oriented**: Indian social dynamics\n\n## Key Components\n\n### Dashboard Component\n```jsx\nimport React, { useState, useEffect } from 'react';\nimport styled from 'styled-components';\n\nconst Dashboard = () => {\n  const [expenses, setExpenses] = useState([]);\n  const [balance, setBalance] = useState(0);\n  \n  return (\n    <DashboardContainer>\n      <BalanceCard>\n        <BalanceAmount>₹{balance}</BalanceAmount>\n        <BalanceLabel>Your Balance</BalanceLabel>\n      </BalanceCard>\n      \n      <QuickActions>\n        <ActionButton>Add Expense</ActionButton>\n        <ActionButton>Settle Up</ActionButton>\n        <ActionButton>Create Group</ActionButton>\n      </QuickActions>\n      \n      <RecentExpenses>\n        {expenses.map(expense => (\n          <ExpenseCard key={expense._id}>\n            <ExpenseTitle>{expense.title}</ExpenseTitle>\n            <ExpenseAmount>₹{expense.amount}</ExpenseAmount>\n          </ExpenseCard>\n        ))}\n      </RecentExpenses>\n    </DashboardContainer>\n  );\n};\n```\n\n## Responsive Design\n\nUsing styled-components for Indian mobile-first design:\n\n```jsx\nconst DashboardContainer = styled.div`\n  padding: 16px;\n  max-width: 400px;\n  margin: 0 auto;\n  \n  @media (min-width: 768px) {\n    max-width: 800px;\n    padding: 24px;\n  }\n`;\n```\n\nThis creates an app that feels native to Indian users while being technically robust.",
                                "isOptional": False
                            }
                        ]
                    },
                    {
                        "sectionId": str(uuid.uuid4()).replace("-", "")[:24],
                        "sectionName": "4. UPI Integration & Payment Processing", 
                        "chapters": [
                            {
                                "chapterId": str(uuid.uuid4()).replace("-", "")[:24],
                                "chapterName": "1. Integrating UPI Payments",
                                "content": "# 1. Integrating UPI Payments\n\n## Understanding UPI in India\n\nUPI (Unified Payments Interface) has revolutionized payments in India. For our PaySplit Pro app, UPI integration is crucial because:\n\n- 💳 **Instant Transfers**: No waiting for bank clearances\n- 📱 **Mobile-first**: Works on any smartphone\n- 🆓 **Zero Charges**: No transaction fees for users\n- 🏦 **Universal**: Works across all Indian banks\n\n## UPI Integration Approach\n\n### For Development\nWe'll use UPI test environments and simulators:\n\n```javascript\n// UPI Payment Request\nconst initiateUPIPayment = async (amount, receiverUPI, description) => {\n  const paymentData = {\n    amount: amount,\n    receiverUPI: receiverUPI,\n    description: description,\n    merchantId: process.env.MERCHANT_ID,\n    orderId: generateOrderId()\n  };\n  \n  try {\n    const response = await axios.post('/api/upi/initiate', paymentData);\n    return response.data;\n  } catch (error) {\n    console.error('UPI Payment Error:', error);\n    throw error;\n  }\n};\n```\n\n### UPI Deep Links\nFor mobile integration, we'll use UPI deep links:\n\n```javascript\nconst generateUPILink = (receiverUPI, amount, description) => {\n  const upiLink = `upi://pay?pa=${receiverUPI}&pn=PaySplitPro&am=${amount}&cu=INR&tn=${encodeURIComponent(description)}`;\n  return upiLink;\n};\n```\n\n## Real-world Implementation\n\nIn production, you'd integrate with:\n- **Razorpay UPI**: For business accounts\n- **Paytm Payment Gateway**: Popular in India\n- **PhonePe Business**: Direct UPI integration\n\nThis makes PaySplit Pro a truly Indian solution that solves real payment friction.",
                                "isOptional": False
                            }
                        ]
                    },
                    {
                        "sectionId": str(uuid.uuid4()).replace("-", "")[:24],
                        "sectionName": "5. Deployment & Production",
                        "chapters": [
                            {
                                "chapterId": str(uuid.uuid4()).replace("-", "")[:24],
                                "chapterName": "1. Deploying Your App",
                                "content": "# 1. Deploying Your PaySplit Pro App\n\n## Deployment Strategy\n\nFor an Indian fintech app like PaySplit Pro, we need:\n\n### Frontend Deployment (Vercel)\n```bash\n# Install Vercel CLI\nnpm i -g vercel\n\n# Deploy frontend\ncd client\nvercel --prod\n```\n\n### Backend Deployment (Railway/Heroku)\n```bash\n# For Railway\nnpm install -g @railway/cli\nrailway login\nrailway deploy\n```\n\n### Database (MongoDB Atlas)\n1. Create MongoDB Atlas cluster\n2. Configure IP whitelist\n3. Update connection strings\n\n## Environment Setup\n\n### Production Environment Variables\n```bash\n# Backend .env\nNODE_ENV=production\nMONGO_URI=mongodb+srv://...\nJWT_SECRET=your-secret\nUPI_MERCHANT_ID=your-merchant-id\n```\n\n## Security Considerations\n\nFor a fintech app in India:\n\n1. **Data Encryption**: All sensitive data encrypted\n2. **HTTPS Only**: SSL certificates mandatory\n3. **Rate Limiting**: Prevent API abuse\n4. **Input Validation**: Sanitize all inputs\n5. **Compliance**: Follow RBI guidelines\n\n## Performance Optimization\n\n```javascript\n// Enable compression\napp.use(compression());\n\n// Set security headers\napp.use(helmet());\n\n// Cache static assets\napp.use(express.static('public', {\n  maxAge: '1d'\n}));\n```\n\n## Monitoring & Analytics\n\nSet up monitoring for:\n- API response times\n- Payment success rates\n- User engagement metrics\n- Error tracking\n\nCongratulations! You've built a production-ready fintech app that could compete with existing solutions in the Indian market. This project demonstrates your ability to build scalable, secure, and user-focused applications - exactly what Indian tech companies are looking for.",
                                "isOptional": False
                            }
                        ]
                    }
                ],
                "__v": 0,
                "meta": "# PaySplit Pro - Your Gateway to Fintech Excellence\n\nWelcome to building PaySplit Pro, a real-world UPI bill-splitting application that solves actual problems faced by millions of Indians every day.\n\n## Why This Project Will Transform Your Career\n\nThis isn't just another tutorial project. PaySplit Pro teaches you:\n\n🏦 **Fintech Skills**: UPI integration, payment processing, financial calculations\n💼 **Industry Experience**: Real-world patterns used by companies like Paytm, PhonePe, and Razorpay\n🚀 **Full-Stack Mastery**: React + Node.js + MongoDB + Payment APIs\n📱 **Mobile-First Design**: Built for Indian smartphone users\n💰 **Career Impact**: Projects like this get you hired at fintech companies with 40-60% salary jumps\n\n## What Makes This Special\n\n- **Real Problem**: Solves actual bill-splitting friction in India\n- **UPI Integration**: Learn the payment system that powers digital India\n- **Scalable Architecture**: Built to handle thousands of users\n- **Production Ready**: Deploy-ready code with security best practices\n- **Portfolio Gold**: Impresses recruiters at Indian startups and MNCs\n\n## Target Outcome\n\nBy the end of this project, you'll have:\n✅ A fully functional fintech application\n✅ Deep understanding of payment systems\n✅ Full-stack development experience\n✅ A portfolio project that gets you interviews\n✅ Skills that command ₹8-15 LPA salaries\n\nLet's build something that could actually become the next big Indian fintech startup!",
                "isEnrolled": False,
                "career_enhancement": {
                    "target_role": "Full Stack Developer",
                    "skill_development": [
                        "Full-stack development with MERN stack",
                        "UPI and payment gateway integration", 
                        "Financial application development",
                        "Mobile-responsive design",
                        "Database design for fintech",
                        "Security best practices",
                        "Production deployment",
                        "API development and testing"
                    ],
                    "hiring_advantages": [
                        "Demonstrates real-world fintech experience",
                        "Shows understanding of Indian payment ecosystem",
                        "Portfolio project that solves actual problems",
                        "Full-stack technical competency",
                        "Understanding of scalable architecture"
                    ],
                    "interview_preparation": {
                        "talking_points": [
                            "UPI integration challenges and solutions",
                            "Database design for financial transactions",
                            "Security considerations in fintech apps",
                            "Scaling for Indian mobile users",
                            "Payment reconciliation and error handling"
                        ],
                        "demo_script": "Start by explaining the bill-splitting problem, demonstrate the UPI integration, walk through the technical architecture, and discuss the business impact.",
                        "technical_questions": [
                            "How did you handle payment security and compliance?",
                            "What were the main technical challenges with UPI integration?", 
                            "How would you scale this for millions of users?",
                            "What would you build next to monetize this app?"
                        ]
                    },
                    "portfolio_guidance": {
                        "github_setup": "Complete repository with clear README, live demo, and technical documentation",
                        "demo_requirements": "Live deployed app, demo video showing UPI flow, technical walkthrough",
                        "presentation_tips": [
                            "Lead with the problem and market opportunity",
                            "Show the UPI integration working live",
                            "Explain the technical architecture clearly",
                            "Discuss potential business applications"
                        ],
                        "resume_bullet_points": [
                            "Built PaySplit Pro - a full-stack UPI bill-splitting app serving Indian users",
                            "Implemented secure UPI payment integration with real-time transaction processing",
                            "Designed scalable MERN stack architecture handling group expenses and settlements",
                            "Deployed production-ready fintech application with security and compliance features"
                        ]
                    },
                    "salary_impact": {
                        "base_range": "6 LPA - 12 LPA",
                        "with_project": "12 LPA - 18 LPA", 
                        "premium_boost": "+30-50% for demonstrated fintech experience",
                        "confidence": "High - fintech projects command premium salaries in India"
                    }
                },
                "success_metrics": {
                    "learning_objectives": [
                        "Master full-stack development with modern technologies",
                        "Understand payment systems and fintech architecture",
                        "Learn mobile-first design for Indian users",
                        "Gain experience with production deployment",
                        "Develop security-first mindset for financial applications"
                    ],
                    "completion_criteria": [
                        "All core features implemented and tested",
                        "UPI integration working in test environment",
                        "Application deployed to production",
                        "Comprehensive documentation completed",
                        "Demo video and presentation prepared"
                    ],
                    "portfolio_readiness": "Excellent - Ready for senior developer portfolios",
                    "career_readiness": "High - Ready for competitive fintech roles"
                }
            }
        }
        
        # Display project summary
        data = project_data.get("data", {})
        
        table = Table(title=f"🌟 Demo Project: {data.get('name', 'Unknown')}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Project Name", data.get("name", "N/A"))
        table.add_row("Description", data.get("description", "N/A")[:80] + "...")
        table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
        table.add_row("Roadmap", data.get("roadmap", "N/A"))
        table.add_row("Sections", str(len(data.get("sections", []))))
        table.add_row("Required Skills", ", ".join(data.get("requiredSkills", [])[:3]) + "...")
        
        console.print(table)
        
        # Show career enhancement info
        career_enhancement = data.get("career_enhancement", {})
        if career_enhancement:
            console.print(f"\n💼 [bold]Career Impact:[/bold]")
            console.print(f"   Target Role: {career_enhancement.get('target_role', 'N/A')}")
            console.print(f"   Skill Development: {len(career_enhancement.get('skill_development', []))} skills")
            console.print(f"   Salary Impact: {career_enhancement.get('salary_impact', {}).get('with_project', 'N/A')}")
        
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tbp_demo_project_paysplit_pro_{timestamp}.json"
            filepath = os.path.join("output", filename)
            
            # Ensure output directory exists
            os.makedirs("output", exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                import json
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"[blue]💾 Demo project saved to: {filepath}[/blue]")
        
        console.print(f"\n[yellow]🎉 Demo project created successfully![/yellow]")
        console.print(f"[green]This static demo shows the exact format for:[/green]")
        console.print("   📊 Complete project structure following API schema")
        console.print("   💰 Career enhancement data with salary impact")
        console.print("   🎯 Real-world fintech project example")
        console.print("   📱 Mobile-first Indian market focus")
        
    except Exception as e:
        console.print(f"[red]❌ Error creating demo project: {str(e)}[/red]")
        raise click.Abort()


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