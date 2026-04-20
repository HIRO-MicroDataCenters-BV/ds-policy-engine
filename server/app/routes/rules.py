"""
Rule CRUD routes with pagination, export, and import.

Includes meta endpoints for discovering available roles and permissions
dynamically (used by the Policy Builder UI), plus export/import for
backup and restore of the full rule set.

Tag: Rules
"""

import csv
import io
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from app.core.dependencies import get_rule_management_service
from app.models.responses import error_response, success_response
from app.models.rule import PaginationParams, RuleCreate, RuleUpdate
from app.services.rule_management import RuleManagementService

logger = logging.getLogger("policy_engine.routes.rules")

router = APIRouter(prefix="/api/v1/rules", tags=["Rules"])


# ---------------------------------------------------------------------------
# Meta endpoints (must be registered BEFORE /{rule_id} to avoid conflicts)
# ---------------------------------------------------------------------------

@router.get("/meta", summary="All rule metadata",
            description="Returns unique roles and permissions derived from existing rules")
async def get_rules_meta(
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Return roles and permissions derived from existing rules."""
    meta = await service.get_meta()
    return success_response(data=meta, message="Rule metadata retrieved")


@router.get("/meta/roles", summary="List known roles",
            description="Returns all unique roles currently defined across rules")
async def list_known_roles(
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Return deduplicated, sorted list of roles from all rules."""
    roles = await service.get_known_roles()
    return success_response(data={"roles": roles}, message="Known roles retrieved")


@router.get("/meta/permissions", summary="List known permissions",
            description="Returns all unique permissions currently defined across rules")
async def list_known_permissions(
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Return deduplicated, sorted list of permissions from all rules."""
    permissions = await service.get_known_permissions()
    return success_response(data={"permissions": permissions}, message="Known permissions retrieved")


# ---------------------------------------------------------------------------
# List & Create
# ---------------------------------------------------------------------------

@router.get("", summary="List rules", description="List all rules with pagination, filtering, and sorting")
async def list_rules(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    role: str | None = Query(default=None),
    enabled: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """List rules with pagination, filtering, sorting, and search."""
    params = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        role=role,
        enabled=enabled,
        search=search,
    )
    rules, pagination = await service.list_rules(params)
    return success_response(
        data={"rules": rules, "pagination": pagination.model_dump()},
        message="Rules retrieved successfully",
    )


@router.post("", summary="Create rule", description="Create a new policy rule", status_code=201)
async def create_rule(
    data: RuleCreate,
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Create a new rule. Roles and permissions are validated for format only."""
    rule = await service.create_rule(data)
    return success_response(data={"rule": rule}, message="Rule created successfully", status_code=201)


# ---------------------------------------------------------------------------
# Single-rule operations (after meta routes to avoid /{rule_id} conflict)
# ---------------------------------------------------------------------------

@router.get("/{rule_id}", summary="Get rule", description="Get a single rule by ID")
async def get_rule(
    rule_id: str,
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Retrieve a single rule by its ID."""
    rule = await service.get_rule(rule_id)
    return success_response(data={"rule": rule}, message="Rule retrieved successfully")


@router.put("/{rule_id}", summary="Update rule", description="Update an existing rule")
async def update_rule(
    rule_id: str,
    data: RuleUpdate,
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Update fields on an existing rule."""
    rule = await service.update_rule(rule_id, data)
    return success_response(data={"rule": rule}, message="Rule updated successfully")


@router.delete("/{rule_id}", summary="Delete rule", description="Delete a rule by ID")
async def delete_rule(
    rule_id: str,
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Delete a rule permanently."""
    await service.delete_rule(rule_id)
    return success_response(message=f"Rule '{rule_id}' deleted successfully")


@router.patch("/{rule_id}/toggle", summary="Toggle rule", description="Enable or disable a rule")
async def toggle_rule(
    rule_id: str,
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Toggle a rule's enabled/disabled state."""
    rule = await service.toggle_rule(rule_id)
    return success_response(data={"rule": rule}, message="Rule toggled successfully")


# ---------------------------------------------------------------------------
# Export / Import
# ---------------------------------------------------------------------------


@router.get("/export/json", summary="Export all rules", description="Export all rules as a JSON backup file")
async def export_rules(
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Export all rules as a JSON document for backup or migration.

    Returns a self-contained JSON with version, timestamp, and all rules.
    This can be saved and later imported via POST /api/v1/rules/import/json.
    """
    from app.core.dependencies import get_rule_repository

    repo = get_rule_repository()
    manifest = await repo.get_manifest()
    rules = manifest.get("rules", [])

    export_data = {
        "version": manifest.get("version", 1),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "last_deployed": manifest.get("last_deployed"),
        "rules_count": len(rules),
        "rules": rules,
    }

    logger.info("Exported %d rules", len(rules))
    return success_response(data=export_data, message=f"Exported {len(rules)} rule(s)")


class ImportRequest(BaseModel):
    """Request body for rule import."""
    rules: list[dict]
    mode: str = "merge"  # "merge" (skip existing) or "replace" (delete all, then insert)


@router.post("/import/json", summary="Import rules from JSON", description="Import rules from a previously exported JSON backup")
async def import_rules(
    body: ImportRequest,
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Import rules from a JSON backup.

    Supports two modes:
    - ``merge``: skip rules whose name already exists, import the rest
    - ``replace``: delete ALL existing rules, then import all from backup

    Args:
        body: ImportRequest with ``rules`` list and ``mode`` ("merge" or "replace").

    Returns:
        JSONResponse: Summary with imported, skipped, and total counts.
    """
    if body.mode not in ("merge", "replace"):
        return error_response(
            code="INVALID_MODE",
            message="Mode must be 'merge' or 'replace'",
            status_code=400,
        )

    from app.core.dependencies import get_rule_repository

    repo = get_rule_repository()
    imported = 0
    skipped = 0
    errors = []

    if body.mode == "replace":
        # Delete all existing rules first
        existing = await repo.list_rules()
        for r in existing:
            await repo.delete_rule(r["id"])
        logger.info("Replace mode: deleted %d existing rules", len(existing))

    for rule in body.rules:
        try:
            # Check for existing by name (merge mode)
            if body.mode == "merge":
                existing = await repo.list_rules()
                if any(r.get("name", "").lower() == rule.get("name", "").lower() for r in existing):
                    skipped += 1
                    continue

            rule_data = {
                "name": rule["name"],
                "description": rule.get("description", ""),
                "role": rule["role"],
                "institute": rule.get("institute", ""),
                "permissions": rule.get("permissions", []),
                "enabled": rule.get("enabled", True),
            }
            await repo.create_rule(rule_data)
            imported += 1
        except Exception as exc:
            errors.append({"rule": rule.get("name", "unknown"), "error": str(exc)})

    logger.info("Imported %d rules (skipped=%d, errors=%d, mode=%s)", imported, skipped, len(errors), body.mode)

    return success_response(
        data={
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
            "total_in_backup": len(body.rules),
        },
        message=f"Imported {imported} rule(s), skipped {skipped}, errors {len(errors)}",
    )


# ---------------------------------------------------------------------------
# CSV Export / Import
# ---------------------------------------------------------------------------

CSV_COLUMNS = ["name", "description", "role", "institute", "permissions", "enabled"]


@router.get(
    "/export/csv",
    summary="Export rules as CSV",
    description="Export all rules as a CSV file for bulk editing in spreadsheets",
    response_class=PlainTextResponse,
)
async def export_rules_csv(
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Export all rules as CSV. Permissions are semicolon-separated."""
    from app.core.dependencies import get_rule_repository

    repo = get_rule_repository()
    manifest = await repo.get_manifest()
    rules = manifest.get("rules", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_COLUMNS)
    for r in rules:
        perms = r.get("permissions", [])
        writer.writerow([
            r.get("name", ""),
            r.get("description", ""),
            r.get("role", ""),
            r.get("institute", ""),
            ";".join(perms) if isinstance(perms, list) else str(perms),
            "true" if r.get("enabled", True) else "false",
        ])

    logger.info("Exported %d rules as CSV", len(rules))
    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=policy-rules-{datetime.now().strftime('%Y-%m-%d')}.csv"},
    )


class CsvImportRequest(BaseModel):
    """Request body for CSV import."""
    csv_content: str
    mode: str = "merge"


@router.post(
    "/import/csv",
    summary="Import rules from CSV",
    description="Import rules from CSV content. Permissions should be semicolon-separated.",
)
async def import_rules_csv(
    body: CsvImportRequest,
    service: RuleManagementService = Depends(get_rule_management_service),
):
    """Import rules from CSV content.

    Expected columns: name, description, role, institute, permissions, enabled.
    Permissions should be semicolon-separated (e.g. catalog:read;catalog:create).
    """
    if body.mode not in ("merge", "replace"):
        return error_response(code="INVALID_MODE", message="Mode must be 'merge' or 'replace'", status_code=400)

    from app.core.dependencies import get_rule_repository

    repo = get_rule_repository()

    # Parse CSV
    reader = csv.DictReader(io.StringIO(body.csv_content))
    parsed_rules = []
    for row in reader:
        perms_raw = row.get("permissions", "")
        perms = [p.strip() for p in perms_raw.split(";") if p.strip()] if perms_raw else []
        enabled_raw = row.get("enabled", "true").lower().strip()
        parsed_rules.append({
            "name": row.get("name", "").strip(),
            "description": row.get("description", "").strip(),
            "role": row.get("role", "").strip(),
            "institute": row.get("institute", "").strip(),
            "permissions": perms,
            "enabled": enabled_raw not in ("false", "0", "no"),
        })

    if not parsed_rules:
        return error_response(code="EMPTY_CSV", message="No rules found in CSV", status_code=400)

    imported = 0
    skipped = 0
    errors = []

    if body.mode == "replace":
        existing = await repo.list_rules()
        for r in existing:
            await repo.delete_rule(r["id"])

    for rule in parsed_rules:
        try:
            if not rule.get("name") or not rule.get("role"):
                errors.append({"rule": rule.get("name", "?"), "error": "Missing name or role"})
                continue
            if body.mode == "merge":
                existing = await repo.list_rules()
                if any(r.get("name", "").lower() == rule["name"].lower() for r in existing):
                    skipped += 1
                    continue
            await repo.create_rule(rule)
            imported += 1
        except Exception as exc:
            errors.append({"rule": rule.get("name", "?"), "error": str(exc)})

    logger.info("CSV import: %d imported, %d skipped, %d errors, mode=%s", imported, skipped, len(errors), body.mode)
    return success_response(
        data={"imported": imported, "skipped": skipped, "errors": errors, "total_in_csv": len(parsed_rules)},
        message=f"Imported {imported} rule(s), skipped {skipped}, errors {len(errors)}",
    )


# ---------------------------------------------------------------------------
# Rego Export
# ---------------------------------------------------------------------------

@router.get(
    "/export/rego",
    summary="Export generated Rego policy",
    description="Export the generated Rego source code for audit, Git versioning, or compliance",
    response_class=PlainTextResponse,
)
async def export_rego():
    """Export the current Rego policy as generated from all rules."""
    from app.core.dependencies import get_policy_deployer_service

    deployer = get_policy_deployer_service()
    rego = await deployer.preview()

    logger.info("Exported Rego policy (%d bytes)", len(rego))
    return PlainTextResponse(
        content=rego,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=policy-{datetime.now().strftime('%Y-%m-%d')}.rego"},
    )
