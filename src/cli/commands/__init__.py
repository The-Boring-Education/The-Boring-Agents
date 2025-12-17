"""
CLI command groups for The Boring Agents.
"""
from .content import content_group
from .interview import interview_group
from .projects import projects_group
from .shiksha import shiksha_group
from .quiz import quiz_group
from .status import status_command

# Set command names explicitly
content_group.name = "content"
interview_group.name = "interview"
projects_group.name = "projects"
shiksha_group.name = "shiksha"
quiz_group.name = "quiz"
status_command.name = "status"

__all__ = [
    "content_group",
    "interview_group",
    "projects_group",
    "shiksha_group",
    "quiz_group",
    "status_command"
]

