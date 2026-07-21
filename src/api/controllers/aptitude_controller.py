"""Aptitude API controller — business logic for aptitude endpoints."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from src.agents.aptitude.constants import TOPIC_REGISTRY
from src.agents.aptitude.validators import validate_batch_payload
from src.agents.aptitude.workflow import AptitudeWorkflow
from src.core.config import config
from src.utils.paths import resolve_under_roots

logger = logging.getLogger(__name__)


class AptitudeController:
    def __init__(self):
        self.workflow = AptitudeWorkflow()

    def _resolve_output_file(self, output_file: str) -> Path:
        """Resolve output_file under configured output/temp directories only."""
        return resolve_under_roots(
            output_file,
            [config.output_dir, config.temp_dir],
        )

    def generate_for_topic(
        self,
        topic: str,
        questions: Optional[List[str]] = None,
        num_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate answers for a single topic."""
        result = self.workflow.process_topic(
            topic=topic,
            questions=questions,
            num_questions=num_questions,
        )

        meta = result["metadata"]
        return {
            "topic": result["topic"],
            "totalQuestions": meta["totalQuestions"],
            "successfulAnswers": meta["successfulAnswers"],
            "outputFile": result.get("outputFile"),
            "message": f"Generated {meta['successfulAnswers']}/{meta['totalQuestions']} answers for '{meta['topicName']}'",
        }

    def generate_batch(
        self,
        topics: List[str],
        num_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate answers for multiple topics."""
        validation = validate_batch_payload(topics)
        if not validation["valid"]:
            raise ValueError(f"Invalid batch payload: {validation['errors']}")

        summary = self.workflow.process_batch(topics, num_questions=num_questions)
        return {
            "totalTopics": summary["totalTopics"],
            "successful": summary["successful"],
            "failed": summary["failed"],
            "message": f"Batch complete: {summary['successful']}/{summary['totalTopics']} topics processed",
        }

    def get_topic_registry(self) -> List[Dict[str, Any]]:
        """Return all registered topics."""
        return TOPIC_REGISTRY

    def generate_study_guide(self, topic: str) -> Dict[str, Any]:
        """Generate a study guide for a single topic."""
        result = self.workflow.generate_study_guide(topic=topic)
        return {
            "topic": result["topic"],
            "content": result["content"],
            "outputFile": result.get("outputFile"),
            "message": f"Generated study guide for '{result['metadata']['topicName']}'",
        }

    def upload_study_guide(
        self,
        output_file: str,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a generated study guide JSON to TBE-Web.

        Reads the JSON file (same format as generate_study_guide output)
        and POSTs { topic, content } to TBE-Web's study guide endpoint.
        """
        resolved = self._resolve_output_file(output_file)

        if not resolved.is_file():
            raise FileNotFoundError(f"Output file not found: {output_file}")

        with open(resolved, encoding="utf-8") as f:
            data = json.load(f)

        topic = data.get("topic")
        content = data.get("content")

        if not topic or not content:
            return {
                "ok": False,
                "message": "File must contain 'topic' and 'content' fields",
            }

        base_url = self._resolve_upload_v1_url(environment)
        url = f"{base_url}/interview-prep/aptitude/study-guide"

        try:
            response = requests.post(
                url,
                json={"topic": topic, "content": content},
                headers={
                    "Content-Type": "application/json",
                    "x-admin-secret": config.admin_secret,
                },
                timeout=30,
            )
            response.raise_for_status()
            resp_data = response.json()
            return {
                "ok": True,
                "message": f"Uploaded study guide for topic '{topic}'",
                "data": resp_data,
            }
        except requests.Timeout:
            return {"ok": False, "message": "Upload timed out"}
        except requests.ConnectionError:
            return {"ok": False, "message": f"Could not connect to {url}"}
        except requests.HTTPError as e:
            return {
                "ok": False,
                "message": f"Upload failed ({e.response.status_code}): {e.response.text[:200]}",
            }
        except Exception as e:
            return {"ok": False, "message": f"Upload failed: {str(e)}"}

    def upload_to_api(
        self,
        output_file: str,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload generated JSON to TBE-Web bulk upload API.

        The output file already contains the exact payload format expected
        by TBE-Web: { topic: "<slug>", questions: [...] }
        """
        resolved = self._resolve_output_file(output_file)

        if not resolved.is_file():
            raise FileNotFoundError(f"Output file not found: {output_file}")

        with open(resolved, encoding="utf-8") as f:
            data = json.load(f)

        upload_payload = {
            "topic": data["topic"],
            "questions": [
                {
                    "question": q["question"],
                    "answer": q["answer"],
                    "options": q.get("options", []),
                    "difficulty": q.get("difficulty", "MEDIUM"),
                    "order": q.get("order", 0),
                }
                for q in data["questions"]
                if q.get("answer")
            ],
        }

        if not upload_payload["questions"]:
            return {"ok": False, "message": "No questions with answers to upload"}

        base_url = self._resolve_upload_v1_url(environment)
        url = f"{base_url}/interview-prep/aptitude/upload"

        try:
            response = requests.post(
                url,
                json=upload_payload,
                headers={
                    "Content-Type": "application/json",
                    "x-admin-secret": config.admin_secret,
                },
                timeout=30,
            )
            response.raise_for_status()
            resp_data = response.json()
            return {
                "ok": True,
                "message": f"Uploaded {len(upload_payload['questions'])} questions for topic '{upload_payload['topic']}'",
                "data": resp_data,
            }
        except requests.Timeout:
            return {"ok": False, "message": "Upload timed out"}
        except requests.ConnectionError:
            return {"ok": False, "message": f"Could not connect to {url}"}
        except requests.HTTPError as e:
            return {
                "ok": False,
                "message": f"Upload failed ({e.response.status_code}): {e.response.text[:200]}",
            }
        except Exception as e:
            return {"ok": False, "message": f"Upload failed: {str(e)}"}

    @staticmethod
    def _resolve_upload_v1_url(environment: Optional[str] = None) -> str:
        """Resolve the target API v1 URL from environment name or config default."""
        return f"{config.get_api_base_url(environment).rstrip('/')}/api/v1"
