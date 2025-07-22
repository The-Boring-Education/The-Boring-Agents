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
from src.agents.interview.interview_sheet_creator import InterviewSheetCreator
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
@click.option('--topic', required=True, help='Technology topic (e.g., JavaScript, React, Python)')
@click.option('--save', is_flag=True, help='Save output to file')
def question_sheet(topic, save):
    """Generate interview question sheet for a technology topic."""
    console.print(f"[green]Generating interview questions for {topic}...[/green]")
    
    agent = InterviewAgent()
    result = agent.create_question_sheet(topic)
    
    # Display summary
    table = Table(title=f"Interview Sheet: {topic}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Topic", result['topic'])
    table.add_row("Roadmap", result['roadmap'])
    table.add_row("Total Questions", str(result['metadata']['total_questions']))
    table.add_row("Estimated Prep Time", result['metadata'].get('estimated_prep_time', 'N/A'))
    
    console.print(table)
    
    # Show question distribution
    questions = result['questions']
    if questions:
        console.print(f"\n📊 [bold]Question Distribution:[/bold]")
        
        # Frequency distribution
        freq_dist = {}
        for q in questions:
            freq = q.get('frequency', 'Asked Frequently')
            freq_dist[freq] = freq_dist.get(freq, 0) + 1
        
        for freq, count in freq_dist.items():
            console.print(f"   {freq}: {count} questions")
        
        # Priority distribution
        priority_dist = {}
        for q in questions:
            priority = q.get('priority', 'Medium')
            priority_dist[priority] = priority_dist.get(priority, 0) + 1
        
        console.print(f"\n🎯 [bold]Priority Distribution:[/bold]")
        for priority, count in priority_dist.items():
            console.print(f"   {priority}: {count} questions")
        
        # Company types
        company_dist = {}
        for q in questions:
            for company_type in q.get('companyTypes', []):
                company_dist[company_type] = company_dist.get(company_type, 0) + 1
        
        console.print(f"\n🏢 [bold]Company Type Distribution:[/bold]")
        for company_type, count in company_dist.items():
            console.print(f"   {company_type}: {count} questions")
    
    if save:
        filename = generate_filename(f"interview_{topic.replace(' ', '_')}")
        filepath = agent.save_content(result, filename)
        console.print(f"[blue]Saved to: {filepath}[/blue]")
    
    # Validate sheet for publication
    sheet_data = {
        "name": f"{topic} Interview Questions",
        "description": f"Comprehensive interview preparation for {topic}",
        "roadmap": result['roadmap'],
        "questions": result['questions']
    }
    
    publication_check = agent.validate_sheet_for_publication(sheet_data)
    
    if publication_check["can_publish"]:
        console.print(f"\n[yellow]Interview sheet generated successfully![/yellow]")
        console.print(f"[green]This sheet contains {len(questions)} high-quality questions with proper categorization.[/green]")
        console.print(f"[green]✅ Sheet is ready for publication to database[/green]")
        
        if publication_check["warnings"]:
            console.print(f"[yellow]⚠️  Warnings: {len(publication_check['warnings'])} issues found but sheet is still valid[/yellow]")
    else:
        console.print(f"\n[red]❌ Sheet validation failed![/red]")
        console.print(f"[red]Reason: {publication_check['reason']}[/red]")
        for error in publication_check["errors"]:
            console.print(f"[red]   • {error}[/red]")
        raise click.Abort()


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


# New Interview Sheet Creation Commands (Phased Approach)
@interview.command()
@click.option('--topic', required=True, help='Interview topic (e.g., JavaScript, React, Python)')
@click.option('--roadmap', default='Tech', help='Roadmap category (Tech, Frontend, Backend, etc.)')
@click.option('--save', is_flag=True, help='Save output to file')
def create_sheet(topic, roadmap, save):
    """Phase 1: Create initial interview sheet structure."""
    console.print(f"[green]🎯 Phase 1: Creating interview sheet for {topic}...[/green]")
    
    try:
        creator = InterviewSheetCreator()
        result = creator.create_interview_sheet(topic, roadmap)
        
        if result["status"] == "success":
            sheet_data = result["sheet_data"]
            
            # Display sheet summary
            table = Table(title=f"📋 Interview Sheet Created: {topic}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Sheet ID", "Will be generated by API")
            table.add_row("Name", sheet_data["name"])
            table.add_row("Slug", sheet_data["slug"])
            table.add_row("Roadmap", sheet_data["roadmap"])
            table.add_row("Questions Count", str(len(sheet_data["questions"])))
            table.add_row("File Path", result["filepath"])
            
            console.print(table)
            
            console.print(f"\n[yellow]✅ Phase 1 Complete![/yellow]")
            console.print(f"[green]📝 Next step: Generate questions list[/green]")
            console.print(f"[blue]Run: python main.py interview generate-questions --topic {topic}[/blue]")
            
        else:
            console.print(f"[red]❌ Error creating sheet: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating interview sheet: {str(e)}[/red]")
        raise click.Abort()


@interview.command()
@click.option('--topic', required=True, help='Interview topic (e.g., JavaScript, React, Python)')
@click.option('--roadmap', default='Tech', help='Roadmap category (Tech, Frontend, Backend, etc.)')
@click.option('--count', default=50, help='Number of questions to generate')
@click.option('--save', is_flag=True, help='Save output to file')
def generate_questions(topic, roadmap, count, save):
    """Phase 2: Generate questions list and save to MDX file."""
    console.print(f"[green]🎯 Phase 2: Generating {count} questions for {topic}...[/green]")
    
    try:
        creator = InterviewSheetCreator()
        result = creator.generate_questions_list(topic, roadmap, count)
        
        if result["status"] == "success":
            console.print(f"\n[yellow]✅ Phase 2 Complete![/yellow]")
            console.print(f"[green]📝 Questions list saved to: {result['mdx_filepath']}[/green]")
            console.print(f"[blue]📋 Review the MDX file and edit questions as needed[/blue]")
            console.print(f"[blue]📋 Then run: python main.py interview generate-answers --mdx-file {result['mdx_filepath']}[/blue]")
            
            # Show questions summary
            questions_content = result["questions_content"]
            question_lines = [line for line in questions_content.split('\n') if line.strip().startswith('- Question:')]
            
            console.print(f"\n📊 [bold]Generated {len(question_lines)} questions[/bold]")
            console.print(f"[green]📝 Review and edit the MDX file before proceeding to Phase 3[/green]")
            
        else:
            console.print(f"[red]❌ Error generating questions: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error generating questions: {str(e)}[/red]")
        raise click.Abort()


@interview.command()
@click.option('--mdx-file', required=True, help='Path to MDX file containing questions')
@click.option('--sheet-file', help='Path to existing sheet JSON file (optional)')
@click.option('--save', is_flag=True, help='Save output to file')
def generate_answers(mdx_file, sheet_file, save):
    """Phase 3: Generate answers for questions from MDX file."""
    console.print(f"[green]🎯 Phase 3: Generating answers from {mdx_file}...[/green]")
    
    try:
        creator = InterviewSheetCreator()
        result = creator.generate_answers_for_questions(mdx_file, sheet_file)
        
        if result["status"] == "success":
            console.print(f"\n[yellow]✅ Phase 3 Complete![/yellow]")
            console.print(f"[green]📝 Complete sheet with answers saved to: {result['filepath']}[/green]")
            console.print(f"[blue]📋 Generated answers for {result['questions_count']} questions[/blue]")
            console.print(f"[blue]📋 Next step: Validate and prepare for database[/blue]")
            console.print(f"[blue]Run: python main.py interview validate-sheet --sheet-file {result['filepath']}[/blue]")
            
        else:
            console.print(f"[red]❌ Error generating answers: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error generating answers: {str(e)}[/red]")
        raise click.Abort()


@interview.command()
@click.option('--sheet-file', required=True, help='Path to sheet JSON file to validate')
@click.option('--save', is_flag=True, help='Save output to file')
def validate_sheet(sheet_file, save):
    """Phase 4: Validate sheet and prepare for database publication."""
    console.print(f"[green]🎯 Phase 4: Validating sheet for publication...[/green]")
    
    try:
        creator = InterviewSheetCreator()
        result = creator.validate_sheet_for_publication(sheet_file)
        
        if result["status"] == "success":
            console.print(f"\n[yellow]✅ Phase 4 Complete![/yellow]")
            console.print(f"[green]📝 Final sheet ready for database: {result['filepath']}[/green]")
            console.print(f"[blue]📋 Sheet validation passed successfully[/blue]")
            console.print(f"[blue]📋 Next step: Publish to database[/blue]")
            console.print(f"[blue]Run: python main.py interview publish-sheet --sheet-file {result['filepath']}[/blue]")
            
            # Show validation summary
            validation = result.get("validation", {})
            if validation.get("is_valid"):
                console.print(f"[green]✅ Sheet structure is valid[/green]")
            else:
                console.print(f"[red]❌ Sheet validation failed:[/red]")
                for error in validation.get("errors", []):
                    console.print(f"[red]   • {error}[/red]")
            
        else:
            console.print(f"[red]❌ Sheet validation failed: {result.get('message', 'Unknown error')}[/red]")
            for error in result.get("errors", []):
                console.print(f"[red]   • {error}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error validating sheet: {str(e)}[/red]")
        raise click.Abort()


@interview.command()
@click.option('--sheet-file', required=True, help='Path to final sheet JSON file to publish')
@click.option('--sheet-id', help='Interview sheet ID (if not provided, will prompt)')
@click.option('--save', is_flag=True, help='Save output to file')
def publish_sheet(sheet_file, sheet_id, save):
    """Phase 5: Add questions to existing interview sheet."""
    console.print(f"[green]🎯 Phase 5: Adding questions to interview sheet...[/green]")
    console.print(f"[yellow]⚠️  This will add questions to: {config.api_base_url}[/yellow]")
    
    if not click.confirm("Continue with adding questions to database?"):
        console.print("Operation cancelled.")
        return
    
    try:
        creator = InterviewSheetCreator()
        result = creator.publish_to_database(sheet_file, sheet_id)
        
        if result["status"] == "success":
            console.print(f"\n[yellow]✅ Phase 5 Complete![/yellow]")
            console.print(f"[green]🎉 Questions added successfully![/green]")
            console.print(f"[blue]📋 Sheet ID: {result['sheet_id']}[/blue]")
            console.print(f"[blue]📋 API URL: {result['api_url']}[/blue]")
            console.print(f"[green]📊 Questions: {result.get('successful_questions', 0)} successful, {result.get('failed_questions', 0)} failed[/green]")
            console.print(f"[green]🎯 All phases completed successfully![/green]")
            
        else:
            console.print(f"[red]❌ Error adding questions: {result.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error adding questions: {str(e)}[/red]")
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
                console.print(f"   Skill Development: {len(career_enhancement.get('skill_development', []))} skills")
                console.print(f"   Salary Impact: {career_enhancement.get('salary_impact', {}).get('with_project', 'N/A')}")
            
            if save:
                filepath = orchestrator.save_project(project_data)
                console.print(f"[blue]✅ Project saved to: {filepath}[/blue]")
            
            console.print(f"\n[yellow]🎉 Project created successfully![/yellow]")
            console.print(f"[green]🤖 AI Auto-Determined:[/green]")
            console.print("   🎯 Domain and tech stack based on your idea")
            console.print("   📊 Difficulty level from project complexity")
            console.print("   👤 Target audience and career path")
            console.print("   🏗️ Complete project structure and roadmap")
            
        else:
            console.print(f"[red]❌ Error creating project: {project_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating project: {str(e)}[/red]")
        raise click.Abort()


@projects.command()
@click.option('--mdx-file', required=True, help='Path to MDX file containing project idea and description')
@click.option('--save', is_flag=True, help='Save output to JSON file')
def create_from_mdx(mdx_file, save):
    """Create a complete project from an MDX file containing idea and description."""
    console.print(f"[green]📄 Creating project from MDX file: {mdx_file}[/green]")
    
    try:
        orchestrator = ProjectOrchestratorAgent()
        project_data = orchestrator.create_project_from_mdx(mdx_file)
        
        # Display project summary
        if project_data.get("status"):
            data = project_data.get("data", {})
            
            table = Table(title=f"📄 Project from MDX: {data.get('name', 'Unknown')}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Project Name", data.get("name", "N/A"))
            table.add_row("Description", data.get("description", "N/A")[:100] + "...")
            table.add_row("Difficulty", data.get("difficultyLevel", "N/A"))
            table.add_row("Roadmap", data.get("roadmap", "N/A"))
            table.add_row("Sections", str(len(data.get("sections", []))))
            table.add_row("Source File", mdx_file)
            
            console.print(table)
            
            if save:
                filepath = orchestrator.save_project(project_data)
                console.print(f"[blue]✅ Project saved to: {filepath}[/blue]")
            
            console.print(f"\n[yellow]🎉 Project created from MDX successfully![/yellow]")
            console.print(f"[green]📝 Parsed from file and enhanced with AI intelligence[/green]")
            
        else:
            console.print(f"[red]❌ Error creating project from MDX: {project_data.get('message', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Error creating project from MDX: {str(e)}[/red]")
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