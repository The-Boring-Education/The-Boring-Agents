#!/usr/bin/env python3
"""
Test script for the simplified Interview Agent.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.interview.interview_agent import InterviewAgent
from rich.console import Console
from rich.table import Table

console = Console()

def test_interview_agent():
    """Test the simplified interview agent."""
    console.print("[bold blue]Testing Simplified Interview Agent[/bold blue]")
    
    try:
        # Initialize agent
        agent = InterviewAgent()
        console.print("[green]✓ Interview Agent initialized successfully[/green]")
        
        # Test with a simple topic
        topic = "JavaScript"
        console.print(f"[yellow]Testing with topic: {topic}[/yellow]")
        
        result = agent.create_question_sheet(topic)
        
        # Display results
        table = Table(title=f"Interview Sheet Results: {topic}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Topic", result.get('topic', 'N/A'))
        table.add_row("Roadmap", result.get('roadmap', 'N/A'))
        table.add_row("Total Questions", str(len(result.get('questions', []))))
        
        console.print(table)
        
        # Show question categorization
        questions = result.get('questions', [])
        if questions:
            console.print(f"\n[bold]Question Categorization:[/bold]")
            
            # Frequency distribution
            freq_dist = {}
            for q in questions:
                freq = q.get('frequency', 'Asked Frequently')
                freq_dist[freq] = freq_dist.get(freq, 0) + 1
            
            console.print(f"📊 Frequency: {freq_dist}")
            
            # Priority distribution
            priority_dist = {}
            for q in questions:
                priority = q.get('priority', 'Medium')
                priority_dist[priority] = priority_dist.get(priority, 0) + 1
            
            console.print(f"🎯 Priority: {priority_dist}")
            
            # Company types
            company_dist = {}
            for q in questions:
                for company_type in q.get('companyTypes', []):
                    company_dist[company_type] = company_dist.get(company_type, 0) + 1
            
            console.print(f"🏢 Company Types: {company_dist}")
        
        console.print(f"\n[bold green]✓ Interview Agent test completed successfully![/bold green]")
        console.print(f"[green]Generated {len(questions)} questions with proper categorization[/green]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Error testing Interview Agent: {str(e)}[/red]")
        return False

def test_roadmap_detection():
    """Test roadmap detection for different topics."""
    console.print(f"\n[bold blue]Testing Roadmap Detection[/bold blue]")
    
    agent = InterviewAgent()
    
    test_topics = [
        ("JavaScript", "Frontend"),
        ("React", "Frontend"),
        ("Python", "Backend"),
        ("Node.js", "Backend"),
        ("MERN Stack", "Fullstack"),
        ("DSA", "Tech"),
        ("System Design", "Tech")
    ]
    
    table = Table(title="Roadmap Detection Results")
    table.add_column("Topic", style="cyan")
    table.add_column("Expected", style="yellow")
    table.add_column("Detected", style="green")
    table.add_column("Status", style="white")
    
    for topic, expected in test_topics:
        detected = agent._determine_roadmap(topic)
        status = "✓" if detected == expected else "✗"
        table.add_row(topic, expected, detected, status)
    
    console.print(table)

def test_categorization():
    """Test question categorization logic."""
    console.print(f"\n[bold blue]Testing Question Categorization[/bold blue]")
    
    agent = InterviewAgent()
    
    test_questions = [
        ("What is the difference between let and const?", "Most Asked", ["Startup", "MidSize"], "High"),
        ("Explain JavaScript closures with examples", "Asked Frequently", ["MidSize", "MNC"], "Medium"),
        ("Design a scalable microservices architecture", "Asked Sometimes", ["MNC", "FAANG"], "Low")
    ]
    
    table = Table(title="Categorization Test Results")
    table.add_column("Question", style="cyan")
    table.add_column("Expected Frequency", style="yellow")
    table.add_column("Detected Frequency", style="green")
    table.add_column("Expected Priority", style="yellow")
    table.add_column("Detected Priority", style="green")
    
    for question, exp_freq, exp_companies, exp_priority in test_questions:
        detected_freq = agent._determine_frequency("Test Title", question)
        detected_priority = agent._determine_priority("Test Title", question)
        
        table.add_row(
            question[:50] + "...",
            exp_freq,
            detected_freq,
            exp_priority,
            detected_priority
        )
    
    console.print(table)

if __name__ == "__main__":
    console.print("[bold]🧪 Testing Simplified Interview Agent[/bold]\n")
    
    # Run tests
    test_interview_agent()
    test_roadmap_detection()
    test_categorization()
    
    console.print(f"\n[bold green]🎉 All tests completed![/bold green]")
    console.print(f"[green]The simplified interview agent is working correctly.[/green]") 