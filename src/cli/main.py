"""
Main CLI entry point for The Boring Agents.
"""
import click
from rich.console import Console
from rich.panel import Panel

# Import environment manager early to ensure env vars are loaded
from src.core.env import get_env_manager, validate_api_keys as validate_env_api_keys
from src.core.config import get_config
from src.utils import setup_logging
from .commands import (
    content_group,
    interview_group,
    projects_group,
    shiksha_group,
    quiz_group,
    status_command
)

console = Console()


@click.group()
@click.option('--log-level', default='INFO', help='Set logging level')
@click.pass_context
def cli(ctx, log_level):
    """The Boring Agents - AI-powered content generation for education."""
    ctx.ensure_object(dict)
    
    # Ensure environment is loaded first
    env_manager = get_env_manager()
    
    # Set up logging with environment-aware level
    env_log_level = env_manager.get("LOG_LEVEL", log_level)
    setup_logging(env_log_level if log_level == 'INFO' else log_level)
    
    # Get config (which will use env manager)
    config = get_config()
    
    # Validate API keys using environment manager
    if not validate_env_api_keys():
        console.print("[red]Error: No API keys configured. Please set up your .env file.[/red]")
        console.print("Copy .env.example to .env and add your API keys.")
        raise click.Abort()
    
    console.print(Panel.fit(
        "[bold blue]The Boring Agents[/bold blue]\n"
        "AI-powered content generation for The Boring Education",
        title="Welcome"
    ))


# Register command groups
cli.add_command(content_group)
cli.add_command(interview_group)
cli.add_command(projects_group)
cli.add_command(shiksha_group)
cli.add_command(quiz_group)
cli.add_command(status_command)

