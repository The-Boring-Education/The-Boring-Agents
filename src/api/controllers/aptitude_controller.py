"""Aptitude API controller — business logic for aptitude endpoints."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests

from src.agents.aptitude.constants import TOPIC_REGISTRY, resolve_topic
from src.agents.aptitude.validators import validate_batch_payload
from src.agents.aptitude.workflow import AptitudeWorkflow
from src.core.config import config

logger = logging.getLogger(__name__)


class AptitudeController:
    def __init__(self):
        self.workflow = AptitudeWorkflow()

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
        api_url: Optional[str] = None,
        admin_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a generated study guide JSON to TBE-Web.

        Reads the JSON file (same format as generate_study_guide output)
        and POSTs { topic, content } to TBE-Web's study guide endpoint.
        """
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Output file not found: {output_file}")

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        topic = data.get("topic")
        content = data.get("content")

        if not topic or not content:
            return {"ok": False, "message": "File must contain 'topic' and 'content' fields"}

        secret = admin_secret or os.environ.get("TBE_ADMIN_SECRET", "TBEAdmin")

        if api_url:
            base_url = api_url.rstrip("/")
            if "/api/v1" not in base_url:
                base_url = f"{base_url}/api/v1"
        else:
            base_url = config.api_v1_url

        url = f"{base_url}/interview-prep/aptitude/study-guide"

        try:
            response = requests.post(
                url,
                json={"topic": topic, "content": content},
                headers={
                    "Content-Type": "application/json",
                    "x-admin-secret": secret,
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
            return {"ok": False, "message": f"Upload failed ({e.response.status_code}): {e.response.text[:200]}"}
        except Exception as e:
            return {"ok": False, "message": f"Upload failed: {str(e)}"}

    def upload_to_api(
        self,
        output_file: str,
        api_url: Optional[str] = None,
        admin_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload generated JSON to TBE-Web bulk upload API.

        The output file already contains the exact payload format expected
        by TBE-Web: { topic: "<slug>", questions: [...] }
        """
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Output file not found: {output_file}")

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        payload = {
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

        if not payload["questions"]:
            return {"ok": False, "message": "No questions with answers to upload"}

        secret = admin_secret or os.environ.get("TBE_ADMIN_SECRET", "TBEAdmin")
        
        # Handle base URL and prefix
        if api_url:
            base_url = api_url.rstrip("/")
            if "/api/v1" not in base_url:
                base_url = f"{base_url}/api/v1"
        else:
            base_url = config.api_v1_url
            
        url = f"{base_url}/interview-prep/aptitude/upload"

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-admin-secret": secret,
                },
                timeout=30,
            )
            response.raise_for_status()
            resp_data = response.json()
            return {
                "ok": True,
                "message": f"Uploaded {len(payload['questions'])} questions for topic '{payload['topic']}'",
                "data": resp_data,
            }
        except requests.Timeout:
            return {"ok": False, "message": "Upload timed out"}
        except requests.ConnectionError:
            return {"ok": False, "message": f"Could not connect to {url}"}
        except requests.HTTPError as e:
            return {"ok": False, "message": f"Upload failed ({e.response.status_code}): {e.response.text[:200]}"}
        except Exception as e:
            return {"ok": False, "message": f"Upload failed: {str(e)}"}
