"""Base pipeline interfaces for orchestrating generation jobs."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from src.core.pipeline.job import Job


class ContentPipeline(ABC):
    """Base contract for generation pipelines."""

    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name

    @abstractmethod
    def run(self, job: Job, **kwargs: Any) -> Dict[str, Any]:
        """Run a generation job and return execution metadata."""
