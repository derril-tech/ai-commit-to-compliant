"""
Release management endpoints for deployment orchestration.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter()
security = HTTPBearer()


class ReleaseCreateRequest(BaseModel):
    """Release creation request."""
    project_id: str
    strategy: str = "blue-green"  # blue-green, canary, rolling, direct
    environment: str = "production"
    sha: Optional[str] = None
    auto_promote: bool = False


class ReleaseResponse(BaseModel):
    """Release response."""
    release_id: str
    project_id: str
    strategy: str
    environment: str
    status: str
    phases: list
    estimated_duration_minutes: int
    created_at: str


class ReleaseStatusResponse(BaseModel):
    """Release status response."""
    release_id: str
    status: str
    current_phase: str
    progress_percentage: float
    phases: list
    health_metrics: Dict[str, Any]
    traffic_split: Dict[str, int] = None
    rollback_available: bool = True


class RollbackRequest(BaseModel):
    """Rollback request."""
    release_id: str
    reason: str = "manual"


@router.post("/create", response_model=ReleaseResponse)
async def create_release(
    request: ReleaseCreateRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(security)
):
    """Create a new release."""
    try:
        from app.services.release_service import ReleaseService
        
        release_service = ReleaseService()
        
        # Create release
        release_result = await release_service.create_release(
            request.project_id,
            request.strategy,
            request.environment,
            request.sha,
            request.auto_promote
        )
        
        # Start background release execution
        background_tasks.add_task(
            execute_release_background,
            release_result["release_id"],
            request.project_id,
            request.strategy,
            request.environment
        )
        
        return release_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create release: {str(e)}")


@router.get("/{release_id}/status", response_model=ReleaseStatusResponse)
async def get_release_status(
    release_id: str,
    token: str = Depends(security)
):
    """Get release status."""
    try:
        from app.services.release_service import ReleaseService
        
        release_service = ReleaseService()
        status = await release_service.get_release_status(release_id)
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get release status: {str(e)}")


@router.post("/{release_id}/promote")
async def promote_release(
    release_id: str,
    token: str = Depends(security)
):
    """Promote a canary release to full deployment."""
    try:
        from app.services.release_service import ReleaseService
        
        release_service = ReleaseService()
        result = await release_service.promote_release(release_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to promote release: {str(e)}")


@router.post("/rollback", response_model=dict)
async def rollback_release(
    request: RollbackRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(security)
):
    """Rollback a release."""
    try:
        from app.services.rollback_service import RollbackService
        
        rollback_service = RollbackService()
        
        # Create rollback plan
        rollback_plan = await rollback_service.create_rollback_plan(
            request.release_id,
            request.reason
        )
        
        # Execute rollback in background
        background_tasks.add_task(
            execute_rollback_background,
            rollback_plan["rollback_id"],
            request.release_id,
            request.reason
        )
        
        return {
            "rollback_id": rollback_plan["rollback_id"],
            "release_id": request.release_id,
            "status": "started",
            "estimated_duration_minutes": rollback_plan.get("estimated_duration_minutes", 3),
            "started_at": datetime.utcnow().isoformat() + "Z",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rollback release: {str(e)}")


@router.get("/{release_id}/health")
async def get_release_health(
    release_id: str,
    token: str = Depends(security)
):
    """Get release health metrics."""
    try:
        from app.services.release_service import ReleaseService
        
        release_service = ReleaseService()
        health = await release_service.check_release_health(release_id)
        
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get release health: {str(e)}")


@router.post("/{release_id}/pause")
async def pause_release(
    release_id: str,
    token: str = Depends(security)
):
    """Pause a release (for canary deployments)."""
    try:
        from app.services.release_service import ReleaseService
        
        release_service = ReleaseService()
        result = await release_service.pause_release(release_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause release: {str(e)}")


@router.post("/{release_id}/resume")
async def resume_release(
    release_id: str,
    token: str = Depends(security)
):
    """Resume a paused release."""
    try:
        from app.services.release_service import ReleaseService
        
        release_service = ReleaseService()
        result = await release_service.resume_release(release_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume release: {str(e)}")


async def execute_release_background(release_id: str, project_id: str, strategy: str, environment: str):
    """Execute release in background."""
    try:
        from app.services.release_service import ReleaseService
        
        release_service = ReleaseService()
        
        print(f"Starting release execution: {release_id}")
        
        # Execute the release strategy
        if strategy == "canary":
            await release_service.execute_canary_release(release_id, project_id, environment)
        elif strategy == "blue-green":
            await release_service.execute_blue_green_release(release_id, project_id, environment)
        elif strategy == "rolling":
            await release_service.execute_rolling_release(release_id, project_id, environment)
        else:
            await release_service.execute_direct_release(release_id, project_id, environment)
        
        print(f"Release execution completed: {release_id}")
        
    except Exception as e:
        print(f"Release execution failed: {release_id}, error: {str(e)}")
        # TODO: Update release status to failed in database


async def execute_rollback_background(rollback_id: str, release_id: str, reason: str):
    """Execute rollback in background."""
    try:
        from app.services.rollback_service import RollbackService
        
        rollback_service = RollbackService()
        
        print(f"Starting rollback execution: {rollback_id}")
        
        # Execute rollback
        rollback_result = await rollback_service.execute_rollback(rollback_id, release_id, reason)
        
        print(f"Rollback execution completed: {rollback_id}")
        
        # Generate postmortem if needed
        if reason in ["health_check_failed", "critical_error"]:
            await rollback_service.generate_postmortem(rollback_id, release_id, rollback_result)
        
    except Exception as e:
        print(f"Rollback execution failed: {rollback_id}, error: {str(e)}")
        # TODO: Update rollback status to failed in database
