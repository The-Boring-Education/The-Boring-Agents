"""Chunk-based pipeline execution helpers."""

import math
from typing import Any, Callable, Dict, List

from src.core.pipeline.base import ContentPipeline
from src.core.pipeline.job import Job
from src.core.session import BaseSessionManager


class ChunkedPipeline(ContentPipeline):
    """Pipeline that executes generation in resumable chunks."""

    def __init__(self, pipeline_name: str):
        super().__init__(pipeline_name=pipeline_name)

    def run(
        self,
        job: Job,
        *,
        session_manager: BaseSessionManager,
        session_id: str,
        chunk_generator: Callable[[Job, int, int], List[Dict[str, Any]]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Run chunk generation from current progress to completion."""
        del kwargs
        job.validate()

        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        metadata = session.setdefault("metadata", {})
        session_manager.initialize_chunk_tracking(
            session_id=session_id,
            target_count=int(metadata.get("target_count", job.target_count)),
            chunk_size=int(metadata.get("chunk_size", job.chunk_size)),
            items_generated=int(metadata.get("items_generated", 0)),
        )
        session = session_manager.get_session(session_id) or session
        metadata = session.setdefault("metadata", {})

        generated_items = int(metadata.get("items_generated", 0))
        target_count = int(metadata.get("target_count", job.target_count))
        chunk_size = int(metadata.get("chunk_size", job.chunk_size))

        chunk_count = math.ceil(max(target_count - generated_items, 0) / chunk_size)
        collected_chunks: List[Dict[str, Any]] = []

        for chunk_index in range(chunk_count):
            remaining = max(target_count - generated_items, 0)
            if remaining <= 0:
                break
            current_chunk_size = min(chunk_size, remaining)
            chunk_items = chunk_generator(job, generated_items, current_chunk_size)

            generated_count = len(chunk_items)
            generated_items += generated_count
            progress = session_manager.increment_generated_items(
                session_id,
                generated_delta=generated_count,
                current_step=(
                    f"Processed chunk {chunk_index + 1}/{chunk_count} "
                    f"({generated_items}/{target_count})"
                ),
            )

            collected_chunks.append(
                {
                    "chunk_index": chunk_index,
                    "requested_count": current_chunk_size,
                    "generated_count": generated_count,
                    "progress": progress,
                    "items": chunk_items,
                }
            )

        return {
            "session_id": session_id,
            "target_count": target_count,
            "chunk_size": chunk_size,
            "items_generated": generated_items,
            "remaining_items": max(target_count - generated_items, 0),
            "chunks": collected_chunks,
            "is_complete": generated_items >= target_count,
        }
