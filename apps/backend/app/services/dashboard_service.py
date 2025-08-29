"""
Dashboard service for generating observability dashboards and SLO monitoring.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.core.config import settings


class SLOStatus(Enum):
    """SLO status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    BREACH = "breach"


class DashboardService:
    """Service for managing dashboards and SLO monitoring."""
    
    async def get_project_dashboard(self, project_id: str, time_range: str = "24h") -> Dict[str, Any]:
        """Get comprehensive project dashboard data."""
        try:
            # Get time range bounds
            end_time = datetime.utcnow()
            if time_range == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=24)
            
            # Gather dashboard data
            dashboard_data = {
                "project_id": project_id,
                "time_range": time_range,
                "generated_at": end_time.isoformat() + "Z",
                "overview": await self._get_overview_metrics(project_id, start_time, end_time),
                "slos": await self._get_slo_status(project_id, start_time, end_time),
                "performance": await self._get_performance_metrics(project_id, start_time, end_time),
                "reliability": await self._get_reliability_metrics(project_id, start_time, end_time),
                "security": await self._get_security_metrics(project_id, start_time, end_time),
                "cost": await self._get_cost_metrics(project_id, start_time, end_time),
                "deployments": await self._get_deployment_metrics(project_id, start_time, end_time),
                "alerts": await self._get_active_alerts(project_id),
                "trends": await self._get_trend_data(project_id, start_time, end_time),
            }
            
            return dashboard_data
            
        except Exception as e:
            raise Exception(f"Failed to get project dashboard: {str(e)}")
    
    async def get_slo_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get SLO-focused dashboard."""
        try:
            slos = await self._get_configured_slos(project_id)
            slo_data = []
            
            for slo in slos:
                slo_status = await self._calculate_slo_status(project_id, slo)
                slo_data.append(slo_status)
            
            return {
                "project_id": project_id,
                "slos": slo_data,
                "overall_slo_health": self._calculate_overall_slo_health(slo_data),
                "burn_rate_alerts": await self._get_burn_rate_alerts(project_id),
                "error_budget_remaining": await self._calculate_error_budget_remaining(project_id),
                "updated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to get SLO dashboard: {str(e)}")
    
    async def create_grafana_dashboard(self, project_id: str, dashboard_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate Grafana dashboard JSON."""
        try:
            if dashboard_type == "slo":
                dashboard_json = await self._generate_slo_grafana_dashboard(project_id)
            elif dashboard_type == "performance":
                dashboard_json = await self._generate_performance_grafana_dashboard(project_id)
            elif dashboard_type == "security":
                dashboard_json = await self._generate_security_grafana_dashboard(project_id)
            else:
                dashboard_json = await self._generate_comprehensive_grafana_dashboard(project_id)
            
            return {
                "project_id": project_id,
                "dashboard_type": dashboard_type,
                "dashboard_json": dashboard_json,
                "grafana_url": f"{settings.GRAFANA_URL}/d/{project_id}-{dashboard_type}",
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to create Grafana dashboard: {str(e)}")
    
    async def configure_alerts(self, project_id: str, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure alerting rules."""
        try:
            alert_rules = []
            
            # SLO burn rate alerts
            if alert_config.get("slo_alerts", True):
                slo_rules = await self._create_slo_alert_rules(project_id)
                alert_rules.extend(slo_rules)
            
            # Performance alerts
            if alert_config.get("performance_alerts", True):
                perf_rules = await self._create_performance_alert_rules(project_id, alert_config)
                alert_rules.extend(perf_rules)
            
            # Error rate alerts
            if alert_config.get("error_alerts", True):
                error_rules = await self._create_error_rate_alert_rules(project_id, alert_config)
                alert_rules.extend(error_rules)
            
            # Security alerts
            if alert_config.get("security_alerts", True):
                security_rules = await self._create_security_alert_rules(project_id)
                alert_rules.extend(security_rules)
            
            # Cost alerts
            if alert_config.get("cost_alerts", True):
                cost_rules = await self._create_cost_alert_rules(project_id, alert_config)
                alert_rules.extend(cost_rules)
            
            return {
                "project_id": project_id,
                "alert_rules": alert_rules,
                "total_rules": len(alert_rules),
                "configured_at": datetime.utcnow().isoformat() + "Z",
                "escalation_policy": alert_config.get("escalation_policy", "default"),
            }
            
        except Exception as e:
            raise Exception(f"Failed to configure alerts: {str(e)}")
    
    async def _get_overview_metrics(self, project_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get overview metrics."""
        # TODO: Query actual metrics from Prometheus/monitoring system
        return {
            "uptime_percentage": 99.95,
            "total_requests": 1_234_567,
            "error_rate": 0.12,
            "p95_latency_ms": 234,
            "deployment_frequency": "2.3/day",
            "mttr_minutes": 4.2,
            "change_failure_rate": 2.1,
            "lead_time_hours": 3.4,
        }
    
    async def _get_slo_status(self, project_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get SLO status for all configured SLOs."""
        # TODO: Query actual SLO data
        return [
            {
                "name": "API Availability",
                "target": 99.9,
                "current": 99.95,
                "status": SLOStatus.HEALTHY.value,
                "error_budget_remaining": 85.2,
                "burn_rate": 0.8,
                "time_to_exhaustion_days": 45,
            },
            {
                "name": "Response Time",
                "target": 500,  # ms
                "current": 234,
                "status": SLOStatus.HEALTHY.value,
                "error_budget_remaining": 92.1,
                "burn_rate": 0.3,
                "time_to_exhaustion_days": 120,
            },
            {
                "name": "Error Rate",
                "target": 1.0,  # %
                "current": 0.12,
                "status": SLOStatus.HEALTHY.value,
                "error_budget_remaining": 88.0,
                "burn_rate": 0.12,
                "time_to_exhaustion_days": 90,
            },
        ]
    
    async def _get_performance_metrics(self, project_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "response_times": {
                "p50": 89,
                "p95": 234,
                "p99": 456,
                "max": 1234,
            },
            "throughput": {
                "requests_per_second": 167.5,
                "peak_rps": 234.1,
                "avg_rps": 145.2,
            },
            "resource_usage": {
                "cpu_utilization": 45.2,
                "memory_utilization": 62.1,
                "disk_utilization": 23.4,
                "network_io_mbps": 12.3,
            },
            "cache_metrics": {
                "hit_rate": 94.2,
                "miss_rate": 5.8,
                "eviction_rate": 0.1,
            },
        }
    
    async def _get_reliability_metrics(self, project_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get reliability metrics."""
        return {
            "uptime": {
                "percentage": 99.95,
                "total_downtime_minutes": 3.6,
                "incidents": 1,
                "mtbf_hours": 168.5,  # Mean Time Between Failures
            },
            "error_rates": {
                "total_errors": 1456,
                "error_rate_percentage": 0.12,
                "5xx_errors": 234,
                "4xx_errors": 1222,
            },
            "recovery": {
                "mttr_minutes": 4.2,  # Mean Time To Recovery
                "mttd_minutes": 1.8,  # Mean Time To Detection
                "rollback_success_rate": 100.0,
            },
        }
    
    async def _get_security_metrics(self, project_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get security metrics."""
        return {
            "vulnerabilities": {
                "critical": 0,
                "high": 1,
                "medium": 3,
                "low": 8,
                "total": 12,
            },
            "compliance": {
                "score": 94.5,
                "passing_checks": 17,
                "failing_checks": 1,
                "waived_checks": 0,
            },
            "secrets": {
                "total_secrets": 23,
                "rotated_this_month": 8,
                "overdue_rotation": 0,
                "drift_detected": 0,
            },
            "access": {
                "failed_auth_attempts": 12,
                "suspicious_activities": 0,
                "privilege_escalations": 0,
            },
        }
    
    async def _get_cost_metrics(self, project_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get cost metrics."""
        return {
            "current_month": {
                "total_cost": 1234.56,
                "compute_cost": 567.89,
                "storage_cost": 234.56,
                "network_cost": 123.45,
                "other_cost": 308.66,
            },
            "trends": {
                "month_over_month_change": 5.2,
                "cost_per_request": 0.0012,
                "cost_per_user": 2.34,
            },
            "optimization": {
                "potential_savings": 156.78,
                "recommendations": 4,
                "efficiency_score": 87.3,
            },
            "budget": {
                "monthly_budget": 1500.00,
                "budget_utilization": 82.3,
                "projected_month_end": 1456.78,
                "days_remaining": 8,
            },
        }
    
    async def _get_deployment_metrics(self, project_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get deployment metrics."""
        return {
            "frequency": {
                "total_deployments": 23,
                "successful_deployments": 22,
                "failed_deployments": 1,
                "rollbacks": 1,
                "success_rate": 95.7,
            },
            "lead_time": {
                "avg_lead_time_hours": 3.4,
                "p95_lead_time_hours": 8.2,
                "fastest_deployment_minutes": 45,
                "slowest_deployment_hours": 12.3,
            },
            "strategies": {
                "blue_green": 8,
                "canary": 12,
                "rolling": 2,
                "direct": 1,
            },
            "quality": {
                "change_failure_rate": 4.3,
                "hotfixes": 2,
                "post_deployment_issues": 1,
            },
        }
    
    async def _get_active_alerts(self, project_id: str) -> List[Dict[str, Any]]:
        """Get active alerts."""
        return [
            {
                "id": "alert-001",
                "name": "High Memory Usage",
                "severity": "warning",
                "status": "firing",
                "started_at": "2024-01-01T10:30:00Z",
                "description": "Memory usage is above 80% threshold",
                "runbook_url": "https://docs.prodsprints.ai/runbooks/memory",
            },
        ]
    
    async def _get_trend_data(self, project_id: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get trend data for charts."""
        # Generate sample time series data
        time_points = []
        current = start_time
        while current <= end_time:
            time_points.append(current.isoformat() + "Z")
            current += timedelta(hours=1)
        
        return {
            "time_points": time_points,
            "response_time_p95": [234 + (i % 50) for i in range(len(time_points))],
            "error_rate": [0.12 + (i % 10) * 0.01 for i in range(len(time_points))],
            "throughput": [167 + (i % 30) for i in range(len(time_points))],
            "cpu_usage": [45 + (i % 20) for i in range(len(time_points))],
            "memory_usage": [62 + (i % 15) for i in range(len(time_points))],
        }
    
    async def _generate_comprehensive_grafana_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Generate comprehensive Grafana dashboard JSON."""
        return {
            "dashboard": {
                "id": None,
                "title": f"ProdSprints - {project_id} Overview",
                "tags": ["prodsprints", "overview", project_id],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "SLO Status",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": f'slo_status{{project="{project_id}"}}',
                                "legendFormat": "{{slo_name}}",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "thresholds"},
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 95},
                                        {"color": "green", "value": 99},
                                    ]
                                },
                                "unit": "percent",
                            }
                        },
                    },
                    {
                        "id": 2,
                        "title": "Response Time P95",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{project="{project_id}"}}[5m]))',
                                "legendFormat": "P95 Response Time",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "s",
                            }
                        },
                    },
                    {
                        "id": 3,
                        "title": "Error Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": f'rate(http_requests_total{{project="{project_id}",status=~"5.."}}[5m]) / rate(http_requests_total{{project="{project_id}"}}[5m]) * 100',
                                "legendFormat": "Error Rate %",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "percent",
                            }
                        },
                    },
                    {
                        "id": 4,
                        "title": "Throughput",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": f'rate(http_requests_total{{project="{project_id}"}}[5m])',
                                "legendFormat": "Requests/sec",
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps",
                            }
                        },
                    },
                ],
                "time": {"from": "now-24h", "to": "now"},
                "refresh": "30s",
            },
            "meta": {
                "type": "db",
                "canSave": True,
                "canEdit": True,
                "canAdmin": True,
                "canStar": True,
                "slug": f"{project_id}-overview",
                "url": f"/d/{project_id}-overview",
                "expires": "0001-01-01T00:00:00Z",
                "created": datetime.utcnow().isoformat() + "Z",
                "updated": datetime.utcnow().isoformat() + "Z",
                "updatedBy": "prodsprints-ai",
                "createdBy": "prodsprints-ai",
                "version": 1,
            },
        }
    
    async def _generate_slo_grafana_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Generate SLO-focused Grafana dashboard."""
        return {
            "dashboard": {
                "id": None,
                "title": f"ProdSprints - {project_id} SLOs",
                "tags": ["prodsprints", "slo", project_id],
                "panels": [
                    {
                        "id": 1,
                        "title": "SLO Compliance",
                        "type": "bargauge",
                        "targets": [
                            {
                                "expr": f'slo_compliance{{project="{project_id}"}}',
                                "legendFormat": "{{slo_name}}",
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "thresholds"},
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 95},
                                        {"color": "green", "value": 99},
                                    ]
                                },
                                "unit": "percent",
                                "min": 0,
                                "max": 100,
                            }
                        },
                    },
                    {
                        "id": 2,
                        "title": "Error Budget Burn Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": f'slo_burn_rate{{project="{project_id}"}}',
                                "legendFormat": "{{slo_name}} Burn Rate",
                            }
                        ],
                    },
                ],
            }
        }
    
    async def _get_configured_slos(self, project_id: str) -> List[Dict[str, Any]]:
        """Get configured SLOs for project."""
        return [
            {
                "name": "API Availability",
                "type": "availability",
                "target": 99.9,
                "window": "30d",
            },
            {
                "name": "Response Time",
                "type": "latency",
                "target": 500,
                "window": "30d",
            },
            {
                "name": "Error Rate",
                "type": "error_rate",
                "target": 1.0,
                "window": "30d",
            },
        ]
    
    async def _calculate_slo_status(self, project_id: str, slo: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate SLO status."""
        # TODO: Query actual metrics
        return {
            "name": slo["name"],
            "type": slo["type"],
            "target": slo["target"],
            "current": 99.95 if slo["type"] == "availability" else (234 if slo["type"] == "latency" else 0.12),
            "status": SLOStatus.HEALTHY.value,
            "error_budget_remaining": 85.2,
            "burn_rate": 0.8,
            "time_to_exhaustion_days": 45,
        }
    
    def _calculate_overall_slo_health(self, slo_data: List[Dict[str, Any]]) -> str:
        """Calculate overall SLO health."""
        if not slo_data:
            return SLOStatus.HEALTHY.value
        
        statuses = [slo["status"] for slo in slo_data]
        
        if SLOStatus.BREACH.value in statuses:
            return SLOStatus.BREACH.value
        elif SLOStatus.CRITICAL.value in statuses:
            return SLOStatus.CRITICAL.value
        elif SLOStatus.WARNING.value in statuses:
            return SLOStatus.WARNING.value
        else:
            return SLOStatus.HEALTHY.value
    
    async def _get_burn_rate_alerts(self, project_id: str) -> List[Dict[str, Any]]:
        """Get burn rate alerts."""
        return []
    
    async def _calculate_error_budget_remaining(self, project_id: str) -> Dict[str, Any]:
        """Calculate error budget remaining."""
        return {
            "availability": 85.2,
            "latency": 92.1,
            "error_rate": 88.0,
        }
    
    async def _create_slo_alert_rules(self, project_id: str) -> List[Dict[str, Any]]:
        """Create SLO alert rules."""
        return [
            {
                "name": f"{project_id}_slo_burn_rate_high",
                "expr": f'slo_burn_rate{{project="{project_id}"}} > 10',
                "for": "5m",
                "severity": "critical",
                "summary": "High SLO burn rate detected",
                "description": "SLO burn rate is consuming error budget too quickly",
            },
            {
                "name": f"{project_id}_slo_error_budget_low",
                "expr": f'slo_error_budget_remaining{{project="{project_id}"}} < 10',
                "for": "1m",
                "severity": "warning",
                "summary": "Low error budget remaining",
                "description": "Error budget is running low, consider reducing deployment frequency",
            },
        ]
    
    async def _create_performance_alert_rules(self, project_id: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create performance alert rules."""
        p95_threshold = config.get("p95_threshold_ms", 500)
        
        return [
            {
                "name": f"{project_id}_high_latency",
                "expr": f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{project="{project_id}"}}[5m])) > {p95_threshold/1000}',
                "for": "5m",
                "severity": "warning",
                "summary": "High response time detected",
                "description": f"P95 response time is above {p95_threshold}ms threshold",
            },
        ]
    
    async def _create_error_rate_alert_rules(self, project_id: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create error rate alert rules."""
        error_threshold = config.get("error_rate_threshold", 5.0)
        
        return [
            {
                "name": f"{project_id}_high_error_rate",
                "expr": f'rate(http_requests_total{{project="{project_id}",status=~"5.."}}[5m]) / rate(http_requests_total{{project="{project_id}"}}[5m]) * 100 > {error_threshold}',
                "for": "2m",
                "severity": "critical",
                "summary": "High error rate detected",
                "description": f"Error rate is above {error_threshold}% threshold",
            },
        ]
    
    async def _create_security_alert_rules(self, project_id: str) -> List[Dict[str, Any]]:
        """Create security alert rules."""
        return [
            {
                "name": f"{project_id}_security_vulnerability_critical",
                "expr": f'security_vulnerabilities{{project="{project_id}",severity="critical"}} > 0',
                "for": "1m",
                "severity": "critical",
                "summary": "Critical security vulnerability detected",
                "description": "Critical security vulnerabilities found in dependencies",
            },
        ]
    
    async def _create_cost_alert_rules(self, project_id: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create cost alert rules."""
        budget_threshold = config.get("budget_threshold_percent", 80)
        
        return [
            {
                "name": f"{project_id}_budget_threshold",
                "expr": f'cost_budget_utilization{{project="{project_id}"}} > {budget_threshold}',
                "for": "1h",
                "severity": "warning",
                "summary": "Budget threshold exceeded",
                "description": f"Monthly budget utilization is above {budget_threshold}%",
            },
        ]
