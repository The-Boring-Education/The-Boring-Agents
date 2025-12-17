"""
Status command.
"""
import click
import os
from rich.console import Console
from rich.table import Table

from src.core.config import config

console = Console()


@click.command()
def status_command():
    """Check system status and configuration."""
    console.print(f"[green]🔍 Checking system status...[/green]")
    
    # Check configuration
    table = Table(title="⚙️ System Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Environment", config.environment)
    table.add_row("API Base URL", config.api_base_url)
    table.add_row("Default Model", config.default_model)
    table.add_row("Max Tokens", str(config.max_tokens))
    table.add_row("Temperature", str(config.temperature))
    table.add_row("Output Directory", config.output_dir)
    
    console.print(table)
    
    # Check API keys
    api_keys_table = Table(title="🔑 API Keys Status")
    api_keys_table.add_column("Service", style="cyan")
    api_keys_table.add_column("Status", style="green")
    
    api_keys_table.add_row("OpenAI", "✅ Configured" if config.openai_api_key else "❌ Missing")
    api_keys_table.add_row("Anthropic", "✅ Configured" if config.anthropic_api_key else "❌ Missing")
    api_keys_table.add_row("HuggingFace", "✅ Configured" if config.huggingface_api_key else "❌ Missing")
    
    console.print(api_keys_table)
    
    # Check output directory
    if os.path.exists(config.output_dir):
        console.print(f"[green]✅ Output directory exists: {config.output_dir}[/green]")
    else:
        console.print(f"[yellow]⚠️  Output directory missing: {config.output_dir}[/yellow]")
        os.makedirs(config.output_dir, exist_ok=True)
        console.print(f"[green]✅ Created output directory[/green]")
    
    console.print(f"\n[green]🎉 System is ready![/green]")

