"""
Run execution and monitoring endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import json

router = APIRouter()
security = HTTPBearer()


class RunResponse(BaseModel):
    """Run response model."""
    id: str
    project_id: str
    kind: str
    status: str
    stage: str
    attempt: int
    logs_ref: str
    metrics: Dict[str, Any]
    policy_result: Dict[str, Any]
    created_at: str
    updated_at: str


class ReadinessCheck(BaseModel):
    """Readiness check item."""
    name: str
    status: str  # passed, failed, pending, waived
    message: str
    remediation_url: str = None
    waivable: bool = True


class ReadinessResponse(BaseModel):
    """Readiness response model."""
    project_id: str
    overall_status: str  # ready, blocked, pending
    checks: List[ReadinessCheck]
    blockers: List[str]
    updated_at: str


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    token: str = Depends(security)
):
    """Get run details."""
    # TODO: Implement run retrieval
    return {
        "id": run_id,
        "project_id": "project-123",
        "kind": "import",
        "status": "running",
        "stage": "audit",
        "attempt": 0,
        "logs_ref": "s3://bucket/logs/run-123.log",
        "metrics": {
            "duration_ms": 45000,
            "files_analyzed": 127,
            "services_detected": 3
        },
        "policy_result": {},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@router.get("/{run_id}/stream")
async def stream_run_progress(
    run_id: str,
    token: str = Depends(security)
):
    """Stream run progress via Server-Sent Events."""
    
    async def event_generator():
        """Generate SSE events for run progress."""
        stages = ["audit", "plan", "validate", "complete"]
        
        for i, stage in enumerate(stages):
            event_data = {
                "run_id": run_id,
                "stage": stage,
                "status": "running" if i < len(stages) - 1 else "done",
                "progress": (i + 1) / len(stages) * 100,
                "message": f"Executing {stage}...",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(2)  # Simulate processing time
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/readiness/{project_id}", response_model=ReadinessResponse)
async def get_readiness(
    project_id: str,
    environment: str = "staging",
    token: str = Depends(security)
):
    """Get project readiness checklist."""
    from app.services.readiness_service import ReadinessService
    
    readiness_service = ReadinessService()
    
    try:
        # Run comprehensive readiness checks
        readiness_result = await readiness_service.run_readiness_checks(project_id, environment)
        
        # Transform to API response format
        checks = []
        for check in readiness_result.get("checks", []):
            checks.append({
                "name": check["name"].replace("_", " ").title(),
                "status": check["status"],
                "message": check["message"],
                "remediation_url": check.get("remediation_url"),
                "waivable": check.get("waivable", True),
                "category": check.get("category", "other"),
                "severity": check.get("severity", "medium"),
            })
        
        return {
            "project_id": project_id,
            "overall_status": readiness_result.get("overall_status", "pending"),
            "overall_score": readiness_result.get("overall_score", 0),
            "checks": checks,
            "blockers": readiness_result.get("blockers", []),
            "updated_at": readiness_result.get("completed_at", datetime.utcnow().isoformat() + "Z"),
            "environment": environment,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get readiness status: {str(e)}")
