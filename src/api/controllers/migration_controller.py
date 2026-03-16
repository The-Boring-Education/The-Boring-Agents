"""Migration controller — orchestrates content export and sync between environments."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from src.core.config import config

logger = logging.getLogger(__name__)


class MigrationController:
    def __init__(self):
        self.output_dir = os.path.join(config.output_dir, "migrations")
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_api_url(self, env: str) -> str:
        if env == "local":
            return config.local_api_base_url
        elif env == "prod":
            return config.prod_api_base_url
        return config.dev_api_base_url

    def _get_admin_secret(self, provided: Optional[str] = None) -> str:
        return provided or os.environ.get("TBE_ADMIN_SECRET", "TBEAdmin")

    # ─── Export ───────────────────────────────────────────────────────────

    def export_content(
        self,
        env: str,
        content_types: List[str],
        filters: Optional[Dict[str, Any]] = None,
        admin_secret: Optional[str] = None,
        save_to_file: bool = True,
    ) -> Dict[str, Any]:
        """Export content from an environment via the export API."""
        base_url = self._get_api_url(env)
        secret = self._get_admin_secret(admin_secret)
        url = f"{base_url}/api/v1/content/export"

        all_exported: Dict[str, Any] = {}
        errors = []

        for ct in content_types:
            export_type = "all" if ct == "all" else ct

            params: Dict[str, str] = {"type": export_type}
            if filters:
                if filters.get("topics"):
                    params["topics"] = ",".join(filters["topics"])
                if filters.get("slugs"):
                    params["slugs"] = ",".join(filters["slugs"])
                if filters.get("roadmap"):
                    params["roadmap"] = filters["roadmap"]
                if filters.get("domain"):
                    params["domain"] = ",".join(filters["domain"])
                if filters.get("difficulty"):
                    params["difficulty"] = ",".join(filters["difficulty"])
                if filters.get("categoryNames"):
                    params["categoryNames"] = ",".join(filters["categoryNames"])

            try:
                response = requests.get(
                    url,
                    params=params,
                    headers={"x-admin-secret": secret},
                    timeout=60,
                )
                response.raise_for_status()
                resp_data = response.json()

                if resp_data.get("status"):
                    exported = resp_data.get("data", {})
                    all_exported[ct] = exported

                    if save_to_file:
                        self._save_export(env, ct, exported)
                else:
                    errors.append(
                        f"{ct}: {resp_data.get('message', 'Unknown error')}"
                    )

            except requests.Timeout:
                errors.append(f"{ct}: Request timed out")
            except requests.ConnectionError:
                errors.append(f"{ct}: Could not connect to {base_url}")
            except requests.HTTPError as e:
                errors.append(f"{ct}: HTTP {e.response.status_code}")
            except Exception as e:
                errors.append(f"{ct}: {str(e)}")

        summary = self._build_export_summary(all_exported)

        return {
            "ok": len(errors) == 0,
            "source": env,
            "sourceUrl": base_url,
            "exported": summary,
            "rawData": all_exported,
            "errors": errors if errors else None,
        }

    def _save_export(self, env: str, content_type: str, data: Dict) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{env}_{content_type}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info("Saved export to %s", filepath)
        return filepath

    def _build_export_summary(self, results: Dict) -> Dict:
        summary = {}
        for ct, data in results.items():
            if not isinstance(data, dict):
                continue
            for key in ("dsaQuestions", "interviewSheets", "aptitude", "quizzes"):
                nested = data.get(key)
                if nested and isinstance(nested, dict) and "count" in nested:
                    summary[key] = nested["count"]
        return summary

    # ─── Sync ─────────────────────────────────────────────────────────────

    def sync_content(
        self,
        env: str,
        content_type: str,
        data: Dict[str, Any],
        dry_run: bool = True,
        admin_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sync content to a target environment via the sync API."""
        base_url = self._get_api_url(env)
        secret = self._get_admin_secret(admin_secret)
        url = f"{base_url}/api/v1/content/sync"

        payload = {
            "type": content_type,
            "dryRun": dry_run,
            "data": data,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "x-admin-secret": secret,
                    "Content-Type": "application/json",
                },
                timeout=120,
            )
            response.raise_for_status()
            resp_data = response.json()

            return {
                "ok": resp_data.get("status", False),
                "target": env,
                "targetUrl": base_url,
                "dryRun": dry_run,
                "contentType": content_type,
                "result": resp_data.get("data"),
                "message": resp_data.get("message", ""),
            }

        except requests.Timeout:
            return {"ok": False, "message": f"Sync timed out for {content_type}"}
        except requests.ConnectionError:
            return {"ok": False, "message": f"Could not connect to {base_url}"}
        except requests.HTTPError as e:
            return {
                "ok": False,
                "message": f"HTTP {e.response.status_code}: {e.response.text[:300]}",
            }
        except Exception as e:
            return {"ok": False, "message": f"Sync failed: {str(e)}"}

    # ─── Full Migration ───────────────────────────────────────────────────

    def migrate(
        self,
        source_env: str,
        target_env: str,
        content_types: List[str],
        dry_run: bool = True,
        filters: Optional[Dict[str, Any]] = None,
        source_admin_secret: Optional[str] = None,
        target_admin_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Full migration: export from source, sync to target."""
        if source_env == target_env:
            return {
                "ok": False,
                "message": "Source and target cannot be the same environment",
            }

        logger.info(
            "Starting migration: %s -> %s (types=%s, dry_run=%s)",
            source_env,
            target_env,
            content_types,
            dry_run,
        )

        # Phase 1: Export
        export_result = self.export_content(
            env=source_env,
            content_types=content_types,
            filters=filters,
            admin_secret=source_admin_secret,
            save_to_file=True,
        )

        if not export_result.get("ok"):
            return {
                "ok": False,
                "message": "Export phase failed",
                "phase": "export",
                "details": export_result,
            }

        raw_data = export_result.get("rawData", {})

        # Phase 2: Sync each content type
        sync_results = {}
        sync_errors = []

        type_data_map = self._prepare_sync_payloads(content_types, raw_data)

        for sync_type, sync_data in type_data_map.items():
            if not sync_data:
                continue

            result = self.sync_content(
                env=target_env,
                content_type=sync_type,
                data=sync_data,
                dry_run=dry_run,
                admin_secret=target_admin_secret,
            )
            sync_results[sync_type] = result
            if not result.get("ok"):
                sync_errors.append(f"{sync_type}: {result.get('message')}")

        return {
            "ok": len(sync_errors) == 0,
            "source": source_env,
            "target": target_env,
            "dryRun": dry_run,
            "export": export_result.get("exported"),
            "sync": sync_results,
            "errors": sync_errors if sync_errors else None,
            "message": (
                "Dry run complete — no changes made"
                if dry_run
                else f"Migration {'completed' if not sync_errors else 'completed with errors'}"
            ),
        }

    def _prepare_sync_payloads(
        self, content_types: List[str], raw_data: Dict
    ) -> Dict[str, Dict]:
        """Convert exported raw data into per-type sync payloads."""
        result = {}

        def extract(data: Dict, key: str, inner: str):
            nested = data.get(key, {})
            if isinstance(nested, dict):
                return nested.get(inner, [])
            return []

        for ct in content_types:
            if ct == "all":
                for ct_key, raw in raw_data.items():
                    if not isinstance(raw, dict):
                        continue
                    if "dsaQuestions" in raw:
                        qs = extract(raw, "dsaQuestions", "questions")
                        if qs:
                            result["dsa-questions"] = {"questions": qs}
                    if "interviewSheets" in raw:
                        ss = extract(raw, "interviewSheets", "sheets")
                        if ss:
                            result["interview-sheets"] = {"sheets": ss}
                    if "aptitude" in raw:
                        ts = extract(raw, "aptitude", "topics")
                        if ts:
                            result["aptitude"] = {"topics": ts}
                    if "quizzes" in raw:
                        qz = extract(raw, "quizzes", "quizzes")
                        if qz:
                            result["quizzes"] = {"quizzes": qz}
                break
            else:
                raw = raw_data.get(ct, {})
                if not isinstance(raw, dict):
                    continue
                if ct == "dsa-questions":
                    qs = extract(raw, "dsaQuestions", "questions")
                    if qs:
                        result[ct] = {"questions": qs}
                elif ct == "interview-sheets":
                    ss = extract(raw, "interviewSheets", "sheets")
                    if ss:
                        result[ct] = {"sheets": ss}
                elif ct == "aptitude":
                    ts = extract(raw, "aptitude", "topics")
                    if ts:
                        result[ct] = {"topics": ts}
                elif ct == "quizzes":
                    qz = extract(raw, "quizzes", "quizzes")
                    if qz:
                        result[ct] = {"quizzes": qz}

        return result

    # ─── List Exports ─────────────────────────────────────────────────────

    def list_exports(self) -> List[Dict[str, Any]]:
        exports = []
        if not os.path.exists(self.output_dir):
            return exports

        for filename in sorted(os.listdir(self.output_dir), reverse=True):
            if filename.startswith("export_") and filename.endswith(".json"):
                filepath = os.path.join(self.output_dir, filename)
                stat = os.stat(filepath)
                parts = filename.replace("export_", "").replace(".json", "").split("_")

                exports.append({
                    "filename": filename,
                    "filepath": filepath,
                    "env": parts[0] if parts else "unknown",
                    "contentType": parts[1] if len(parts) > 1 else "unknown",
                    "sizeBytes": stat.st_size,
                    "createdAt": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                })

        return exports

    def load_export_file(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.output_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Export file not found: {filename}")

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
