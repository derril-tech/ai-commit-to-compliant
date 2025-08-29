"""
Dashboard and observability endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.services.dashboard_service import DashboardService

router = APIRouter()
security = HTTPBearer()
dashboard_service = DashboardService()


class AlertConfigRequest(BaseModel):
    """Alert configuration request."""
    slo_alerts: bool = True
    performance_alerts: bool = True
    error_alerts: bool = True
    security_alerts: bool = True
    cost_alerts: bool = True
    p95_threshold_ms: int = 500
    error_rate_threshold: float = 5.0
    budget_threshold_percent: int = 80
    escalation_policy: str = "default"


class DashboardResponse(BaseModel):
    """Dashboard response."""
    project_id: str
    time_range: str
    generated_at: str
    overview: Dict[str, Any]
    slos: List[Dict[str, Any]]
    performance: Dict[str, Any]
    reliability: Dict[str, Any]
    security: Dict[str, Any]
    cost: Dict[str, Any]
    deployments: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    trends: Dict[str, Any]


class SLODashboardResponse(BaseModel):
    """SLO dashboard response."""
    project_id: str
    slos: List[Dict[str, Any]]
    overall_slo_health: str
    burn_rate_alerts: List[Dict[str, Any]]
    error_budget_remaining: Dict[str, Any]
    updated_at: str


@router.get("/{project_id}", response_model=DashboardResponse)
async def get_project_dashboard(
    project_id: str,
    time_range: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    token: str = Depends(security)
):
    """Get comprehensive project dashboard."""
    try:
        dashboard = await dashboard_service.get_project_dashboard(project_id, time_range)
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


@router.get("/{project_id}/slo", response_model=SLODashboardResponse)
async def get_slo_dashboard(
    project_id: str,
    token: str = Depends(security)
):
    """Get SLO-focused dashboard."""
    try:
        slo_dashboard = await dashboard_service.get_slo_dashboard(project_id)
        return slo_dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SLO dashboard: {str(e)}")


@router.post("/{project_id}/grafana")
async def create_grafana_dashboard(
    project_id: str,
    dashboard_type: str = Query("comprehensive", regex="^(comprehensive|slo|performance|security)$"),
    token: str = Depends(security)
):
    """Create Grafana dashboard JSON."""
    try:
        grafana_dashboard = await dashboard_service.create_grafana_dashboard(project_id, dashboard_type)
        return grafana_dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Grafana dashboard: {str(e)}")


@router.post("/{project_id}/alerts")
async def configure_alerts(
    project_id: str,
    alert_config: AlertConfigRequest,
    token: str = Depends(security)
):
    """Configure alerting rules."""
    try:
        alert_result = await dashboard_service.configure_alerts(
            project_id, 
            alert_config.dict()
        )
        return alert_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure alerts: {str(e)}")


@router.get("/{project_id}/metrics/overview")
async def get_overview_metrics(
    project_id: str,
    token: str = Depends(security)
):
    """Get overview metrics summary."""
    try:
        dashboard = await dashboard_service.get_project_dashboard(project_id, "24h")
        return {
            "project_id": project_id,
            "overview": dashboard["overview"],
            "slo_health": dashboard_service._calculate_overall_slo_health(dashboard["slos"]),
            "active_alerts": len(dashboard["alerts"]),
            "updated_at": dashboard["generated_at"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overview metrics: {str(e)}")


@router.get("/{project_id}/metrics/performance")
async def get_performance_metrics(
    project_id: str,
    time_range: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    token: str = Depends(security)
):
    """Get detailed performance metrics."""
    try:
        dashboard = await dashboard_service.get_project_dashboard(project_id, time_range)
        return {
            "project_id": project_id,
            "time_range": time_range,
            "performance": dashboard["performance"],
            "trends": dashboard["trends"],
            "updated_at": dashboard["generated_at"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/{project_id}/metrics/cost")
async def get_cost_metrics(
    project_id: str,
    time_range: str = Query("30d", regex="^(7d|30d|90d)$"),
    token: str = Depends(security)
):
    """Get cost metrics and optimization recommendations."""
    try:
        dashboard = await dashboard_service.get_project_dashboard(project_id, time_range)
        return {
            "project_id": project_id,
            "time_range": time_range,
            "cost": dashboard["cost"],
            "updated_at": dashboard["generated_at"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost metrics: {str(e)}")


@router.get("/{project_id}/metrics/security")
async def get_security_metrics(
    project_id: str,
    token: str = Depends(security)
):
    """Get security metrics and compliance status."""
    try:
        dashboard = await dashboard_service.get_project_dashboard(project_id, "7d")
        return {
            "project_id": project_id,
            "security": dashboard["security"],
            "updated_at": dashboard["generated_at"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get security metrics: {str(e)}")


@router.get("/{project_id}/alerts")
async def get_active_alerts(
    project_id: str,
    severity: Optional[str] = Query(None, regex="^(critical|warning|info)$"),
    token: str = Depends(security)
):
    """Get active alerts for project."""
    try:
        dashboard = await dashboard_service.get_project_dashboard(project_id, "1h")
        alerts = dashboard["alerts"]
        
        if severity:
            alerts = [alert for alert in alerts if alert.get("severity") == severity]
        
        return {
            "project_id": project_id,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "updated_at": dashboard["generated_at"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post("/{project_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    project_id: str,
    alert_id: str,
    token: str = Depends(security)
):
    """Acknowledge an alert."""
    try:
        # TODO: Implement actual alert acknowledgment
        return {
            "project_id": project_id,
            "alert_id": alert_id,
            "acknowledged": True,
            "acknowledged_at": "2024-01-01T00:00:00Z",
            "acknowledged_by": "user",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/{project_id}/alerts/{alert_id}/resolve")
async def resolve_alert(
    project_id: str,
    alert_id: str,
    resolution_note: Optional[str] = None,
    token: str = Depends(security)
):
    """Resolve an alert."""
    try:
        # TODO: Implement actual alert resolution
        return {
            "project_id": project_id,
            "alert_id": alert_id,
            "resolved": True,
            "resolved_at": "2024-01-01T00:00:00Z",
            "resolved_by": "user",
            "resolution_note": resolution_note,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/{project_id}/health")
async def get_health_summary(
    project_id: str,
    token: str = Depends(security)
):
    """Get overall health summary."""
    try:
        dashboard = await dashboard_service.get_project_dashboard(project_id, "1h")
        slo_dashboard = await dashboard_service.get_slo_dashboard(project_id)
        
        # Calculate health score
        slo_health_score = 100 if slo_dashboard["overall_slo_health"] == "healthy" else (
            75 if slo_dashboard["overall_slo_health"] == "warning" else 
            25 if slo_dashboard["overall_slo_health"] == "critical" else 0
        )
        
        security_score = dashboard["security"]["compliance"]["score"]
        performance_score = min(100, max(0, 100 - (dashboard["performance"]["response_times"]["p95"] - 200) / 10))
        
        overall_health_score = (slo_health_score + security_score + performance_score) / 3
        
        return {
            "project_id": project_id,
            "overall_health_score": round(overall_health_score, 1),
            "slo_health": slo_dashboard["overall_slo_health"],
            "active_incidents": len([a for a in dashboard["alerts"] if a.get("severity") == "critical"]),
            "security_score": security_score,
            "performance_score": round(performance_score, 1),
            "uptime_percentage": dashboard["reliability"]["uptime"]["percentage"],
            "error_rate": dashboard["reliability"]["error_rates"]["error_rate_percentage"],
            "updated_at": dashboard["generated_at"],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get health summary: {str(e)}")