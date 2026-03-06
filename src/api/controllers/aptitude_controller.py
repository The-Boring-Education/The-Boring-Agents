"""Aptitude API controller — business logic for aptitude endpoints."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests

from src.agents.aptitude.constants import TOPIC_REGISTRY, get_topic_info, validate_topic_name
from src.agents.aptitude.validators import validate_batch_payload
from src.agents.aptitude.workflow import AptitudeWorkflow
from src.core.config import config

logger = logging.getLogger(__name__)


class AptitudeController:
    def __init__(self):
        self.workflow = AptitudeWorkflow()

    def generate_for_topic(self, topic_name: str, questions: List[str],
                           category: Optional[str] = None,
                           sub_category: Optional[str] = None) -> Dict[str, Any]:
        """Generate answers for a single topic."""
        result = self.workflow.process_topic(
            topic_name=topic_name,
            questions=questions,
            category=category,
            sub_category=sub_category,
        )
        return {
            "topic": topic_name,
            "formatType": result["topic"]["answerFormatType"],
            "totalQuestions": result["metadata"]["totalQuestions"],
            "successfulAnswers": result["metadata"]["successfulAnswers"],
            "outputFile": result.get("outputFile"),
            "message": f"Generated {result['metadata']['successfulAnswers']}/{result['metadata']['totalQuestions']} answers",
        }

    def generate_batch(self, topics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answers for multiple topics."""
        validation = validate_batch_payload(topics)
        if not validation["valid"]:
            raise ValueError(f"Invalid batch payload: {validation['errors']}")

        summary = self.workflow.process_batch(topics)
        return {
            "totalTopics": summary["totalTopics"],
            "successful": summary["successful"],
            "failed": summary["failed"],
            "skipped": summary["skipped"],
            "message": f"Batch complete: {summary['successful']}/{summary['totalTopics']} topics processed",
        }

    def get_topic_registry(self) -> List[Dict[str, Any]]:
        """Return all registered topics."""
        return TOPIC_REGISTRY

    def upload_to_api(self, output_file: str, api_url: Optional[str] = None,
                      admin_secret: str = "TBEAdmin") -> Dict[str, Any]:
        """Upload generated JSON to TBE-Web API."""
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Output file not found: {output_file}")

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        topic_data = data["topic"]
        questions = data["questions"]

        payload = {
            "topics": [{
                "name": topic_data["name"],
                "slug": topic_data["slug"],
                "category": topic_data["category"],
                "subCategory": topic_data["subCategory"],
                "answerFormatType": topic_data["answerFormatType"],
                "questions": [
                    {
                        "question": q["question"],
                        "answer": q["answer"],
                        "difficulty": q.get("difficulty", "MEDIUM"),
                        "order": q.get("order", 0),
                    }
                    for q in questions if q.get("answer")
                ],
            }]
        }

        base_url = api_url or config.api_base_url
        url = f"{base_url}/api/v1/aptitude/upload"

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-admin-secret": admin_secret,
                },
                timeout=30,
            )
            response.raise_for_status()
            return {"ok": True, "message": "Upload successful", "data": response.json()}
        except requests.Timeout:
            return {"ok": False, "message": "Upload timed out"}
        except requests.ConnectionError:
            return {"ok": False, "message": f"Could not connect to {url}"}
        except Exception as e:
            return {"ok": False, "message": f"Upload failed: {str(e)}"}
