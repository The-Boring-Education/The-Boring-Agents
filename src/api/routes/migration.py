"""Content migration routes — export from dev, sync to prod."""

import logging

from fastapi import APIRouter, HTTPException

from src.api.controllers.migration_controller import MigrationController
from src.api.models.migration_models import (
    ExportRequest,
    MigrateRequest,
    MigrationStatus,
    SyncRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/migration", tags=["Content Migration"])
controller = MigrationController()


@router.post("/migrate", response_model=MigrationStatus)
def migrate_content(payload: MigrateRequest):
    """
    Full migration: export content from source environment and sync to target.

    Default: dry_run=True (preview only). Set dry_run=False to execute.
    Default: source=dev, target=prod.
    """
    try:
        content_types = [ct.value for ct in payload.content_types]

        result = controller.migrate(
            source_env=payload.source_env,
            target_env=payload.target_env,
            content_types=content_types,
            dry_run=payload.dry_run,
            filters=payload.filters,
            source_admin_secret=payload.source_admin_secret,
            target_admin_secret=payload.target_admin_secret,
        )

        return MigrationStatus(
            ok=result.get("ok", False),
            message=result.get("message", ""),
            dry_run=payload.dry_run,
            source=payload.source_env,
            target=payload.target_env,
            results=result,
        )
    except Exception as e:
        logger.error("Migration failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
def export_content(payload: ExportRequest):
    """Export content from an environment and save to JSON files."""
    try:
        content_types = [ct.value for ct in payload.content_types]

        result = controller.export_content(
            env=payload.env,
            content_types=content_types,
            filters=payload.filters,
            admin_secret=payload.admin_secret,
            save_to_file=payload.save_to_file,
        )

        return result
    except Exception as e:
        logger.error("Export failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
def sync_content(payload: SyncRequest):
    """
    Sync content to a target environment.

    Reads from provided payload data.
    Default: dry_run=True (preview only).
    """
    try:
        result = controller.sync_content(
            env=payload.env,
            content_type=payload.content_type.value,
            data=payload.data,
            dry_run=payload.dry_run,
            admin_secret=payload.admin_secret,
        )

        return result
    except Exception as e:
        logger.error("Sync failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exports")
def list_exports():
    """List all previously saved export files."""
    return {"exports": controller.list_exports()}


@router.get("/exports/{filename}")
def get_export(filename: str):
    """Load and return a previously saved export file."""
    try:
        data = controller.load_export_file(filename)
        return {"ok": True, "filename": filename, "data": data}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Export file not found: {filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
def migration_status():
    """Health check and configuration info for the migration system."""
    from src.core.config import config as app_config

    return {
        "ok": True,
        "environment": app_config.environment,
        "endpoints": {
            "local": app_config.local_api_base_url,
            "dev": app_config.dev_api_base_url,
            "prod": app_config.prod_api_base_url,
        },
        "activeApiUrl": app_config.api_base_url,
        "exportDir": controller.output_dir,
        "exportCount": len(controller.list_exports()),
    }
