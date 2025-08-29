"""
Cost optimization service with recommendations and budget management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.core.config import settings


class CostCategory(Enum):
    """Cost categories."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECURITY = "security"
    OTHER = "other"


class OptimizationPriority(Enum):
    """Optimization priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CostService:
    """Service for cost optimization and budget management."""
    
    async def analyze_costs(self, project_id: str, time_period: str = "30d") -> Dict[str, Any]:
        """Analyze project costs and identify optimization opportunities."""
        try:
            # Get cost data for the specified period
            cost_data = await self._get_cost_data(project_id, time_period)
            
            # Analyze cost trends
            trends = await self._analyze_cost_trends(cost_data)
            
            # Identify optimization opportunities
            optimizations = await self._identify_optimizations(project_id, cost_data)
            
            # Calculate efficiency metrics
            efficiency = await self._calculate_efficiency_metrics(project_id, cost_data)
            
            # Generate cost forecast
            forecast = await self._generate_cost_forecast(cost_data, trends)
            
            return {
                "project_id": project_id,
                "analysis_id": f"cost-analysis-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "time_period": time_period,
                "current_costs": cost_data,
                "trends": trends,
                "optimizations": optimizations,
                "efficiency_metrics": efficiency,
                "forecast": forecast,
                "analyzed_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to analyze costs: {str(e)}")
    
    async def get_optimization_recommendations(self, project_id: str) -> Dict[str, Any]:
        """Get detailed cost optimization recommendations."""
        try:
            cost_data = await self._get_cost_data(project_id, "30d")
            recommendations = []
            
            # Compute optimizations
            compute_recs = await self._get_compute_optimizations(project_id, cost_data)
            recommendations.extend(compute_recs)
            
            # Storage optimizations
            storage_recs = await self._get_storage_optimizations(project_id, cost_data)
            recommendations.extend(storage_recs)
            
            # Database optimizations
            database_recs = await self._get_database_optimizations(project_id, cost_data)
            recommendations.extend(database_recs)
            
            # Network optimizations
            network_recs = await self._get_network_optimizations(project_id, cost_data)
            recommendations.extend(network_recs)
            
            # Sort by potential savings
            recommendations.sort(key=lambda x: x.get("potential_savings", 0), reverse=True)
            
            total_potential_savings = sum(rec.get("potential_savings", 0) for rec in recommendations)
            
            return {
                "project_id": project_id,
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "total_potential_savings": total_potential_savings,
                "potential_savings_percentage": self._calculate_savings_percentage(cost_data, total_potential_savings),
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to get optimization recommendations: {str(e)}")
    
    async def create_budget_alert(self, project_id: str, budget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create budget alert configuration."""
        try:
            alert_config = {
                "project_id": project_id,
                "alert_id": f"budget-alert-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "budget_amount": budget_config.get("budget_amount", 1000.0),
                "currency": budget_config.get("currency", "USD"),
                "period": budget_config.get("period", "monthly"),
                "thresholds": budget_config.get("thresholds", [50, 80, 100]),
                "notification_channels": budget_config.get("notification_channels", ["email"]),
                "enabled": budget_config.get("enabled", True),
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            
            # TODO: Store alert configuration in database
            # TODO: Set up actual alerting mechanism
            
            return alert_config
            
        except Exception as e:
            raise Exception(f"Failed to create budget alert: {str(e)}")
    
    async def get_cost_breakdown(self, project_id: str, time_period: str = "30d") -> Dict[str, Any]:
        """Get detailed cost breakdown by service and category."""
        try:
            cost_data = await self._get_cost_data(project_id, time_period)
            
            # Break down costs by category
            category_breakdown = {}
            service_breakdown = {}
            
            for service, cost_info in cost_data.get("services", {}).items():
                service_cost = cost_info.get("total_cost", 0)
                service_category = cost_info.get("category", CostCategory.OTHER.value)
                
                # Category breakdown
                if service_category not in category_breakdown:
                    category_breakdown[service_category] = {
                        "total_cost": 0,
                        "services": [],
                        "percentage": 0,
                    }
                
                category_breakdown[service_category]["total_cost"] += service_cost
                category_breakdown[service_category]["services"].append(service)
                
                # Service breakdown
                service_breakdown[service] = {
                    "cost": service_cost,
                    "category": service_category,
                    "usage_metrics": cost_info.get("usage_metrics", {}),
                    "cost_per_unit": cost_info.get("cost_per_unit", 0),
                }
            
            # Calculate percentages
            total_cost = cost_data.get("total_cost", 0)
            for category in category_breakdown:
                if total_cost > 0:
                    category_breakdown[category]["percentage"] = round(
                        (category_breakdown[category]["total_cost"] / total_cost) * 100, 2
                    )
            
            return {
                "project_id": project_id,
                "time_period": time_period,
                "total_cost": total_cost,
                "category_breakdown": category_breakdown,
                "service_breakdown": service_breakdown,
                "top_cost_drivers": self._get_top_cost_drivers(service_breakdown),
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to get cost breakdown: {str(e)}")
    
    async def _get_cost_data(self, project_id: str, time_period: str) -> Dict[str, Any]:
        """Get cost data for the specified time period."""
        # TODO: Integrate with actual cloud provider billing APIs
        # For now, return mock cost data
        
        return {
            "total_cost": 1234.56,
            "currency": "USD",
            "period": time_period,
            "services": {
                "compute": {
                    "total_cost": 567.89,
                    "category": CostCategory.COMPUTE.value,
                    "usage_metrics": {
                        "instance_hours": 720,
                        "cpu_hours": 2880,
                        "memory_gb_hours": 5760,
                    },
                    "cost_per_unit": 0.197,
                },
                "database": {
                    "total_cost": 234.56,
                    "category": CostCategory.DATABASE.value,
                    "usage_metrics": {
                        "instance_hours": 720,
                        "storage_gb": 100,
                        "iops": 1000,
                    },
                    "cost_per_unit": 0.326,
                },
                "storage": {
                    "total_cost": 123.45,
                    "category": CostCategory.STORAGE.value,
                    "usage_metrics": {
                        "storage_gb": 500,
                        "requests": 1000000,
                        "data_transfer_gb": 100,
                    },
                    "cost_per_unit": 0.023,
                },
                "network": {
                    "total_cost": 89.12,
                    "category": CostCategory.NETWORK.value,
                    "usage_metrics": {
                        "data_transfer_gb": 1000,
                        "load_balancer_hours": 720,
                    },
                    "cost_per_unit": 0.09,
                },
                "monitoring": {
                    "total_cost": 45.67,
                    "category": CostCategory.MONITORING.value,
                    "usage_metrics": {
                        "metrics_ingested": 10000000,
                        "logs_ingested_gb": 50,
                    },
                    "cost_per_unit": 0.0046,
                },
                "security": {
                    "total_cost": 173.87,
                    "category": CostCategory.SECURITY.value,
                    "usage_metrics": {
                        "scans_performed": 100,
                        "secrets_stored": 50,
                    },
                    "cost_per_unit": 1.74,
                },
            },
        }
    
    async def _analyze_cost_trends(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost trends over time."""
        # TODO: Implement actual trend analysis
        # For now, return mock trend data
        
        return {
            "month_over_month_change": 5.2,
            "trend_direction": "increasing",
            "seasonal_patterns": {
                "peak_months": ["November", "December"],
                "low_months": ["February", "March"],
            },
            "cost_volatility": "low",
            "growth_rate": 2.1,
        }
    
    async def _identify_optimizations(self, project_id: str, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify cost optimization opportunities."""
        optimizations = []
        
        services = cost_data.get("services", {})
        
        # Check compute optimization opportunities
        compute_cost = services.get("compute", {}).get("total_cost", 0)
        if compute_cost > 400:
            optimizations.append({
                "category": CostCategory.COMPUTE.value,
                "type": "rightsizing",
                "title": "Rightsize Compute Instances",
                "description": "Current instances appear oversized based on utilization metrics",
                "potential_savings": 150.00,
                "priority": OptimizationPriority.HIGH.value,
                "effort": "medium",
                "implementation_time": "1-2 weeks",
            })
        
        # Check storage optimization opportunities
        storage_cost = services.get("storage", {}).get("total_cost", 0)
        if storage_cost > 100:
            optimizations.append({
                "category": CostCategory.STORAGE.value,
                "type": "lifecycle_policy",
                "title": "Implement Storage Lifecycle Policies",
                "description": "Move infrequently accessed data to cheaper storage tiers",
                "potential_savings": 45.00,
                "priority": OptimizationPriority.MEDIUM.value,
                "effort": "low",
                "implementation_time": "1 week",
            })
        
        # Check database optimization opportunities
        db_cost = services.get("database", {}).get("total_cost", 0)
        if db_cost > 200:
            optimizations.append({
                "category": CostCategory.DATABASE.value,
                "type": "reserved_instances",
                "title": "Purchase Database Reserved Instances",
                "description": "Save up to 40% with 1-year reserved instance commitment",
                "potential_savings": 93.82,
                "priority": OptimizationPriority.HIGH.value,
                "effort": "low",
                "implementation_time": "immediate",
            })
        
        return optimizations
    
    async def _calculate_efficiency_metrics(self, project_id: str, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost efficiency metrics."""
        # TODO: Integrate with actual usage and performance metrics
        # For now, return mock efficiency data
        
        return {
            "cost_per_user": 2.34,
            "cost_per_request": 0.0012,
            "cost_per_transaction": 0.045,
            "resource_utilization": {
                "cpu": 65.2,
                "memory": 72.8,
                "storage": 45.6,
                "network": 23.4,
            },
            "efficiency_score": 78.5,
            "benchmark_comparison": {
                "industry_average": 72.1,
                "percentile": 68,
            },
        }
    
    async def _generate_cost_forecast(self, cost_data: Dict[str, Any], trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cost forecast based on trends."""
        current_monthly_cost = cost_data.get("total_cost", 0)
        growth_rate = trends.get("growth_rate", 0) / 100
        
        # Generate 12-month forecast
        forecast_months = []
        for month in range(1, 13):
            projected_cost = current_monthly_cost * (1 + growth_rate) ** month
            forecast_months.append({
                "month": month,
                "projected_cost": round(projected_cost, 2),
            })
        
        return {
            "forecast_period": "12 months",
            "monthly_projections": forecast_months,
            "annual_projection": sum(month["projected_cost"] for month in forecast_months),
            "confidence_level": 75,
            "assumptions": [
                f"Monthly growth rate: {trends.get('growth_rate', 0)}%",
                "No major architecture changes",
                "Current usage patterns continue",
            ],
        }
    
    async def _get_compute_optimizations(self, project_id: str, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get compute-specific optimization recommendations."""
        recommendations = []
        
        compute_service = cost_data.get("services", {}).get("compute", {})
        compute_cost = compute_service.get("total_cost", 0)
        
        if compute_cost > 300:
            recommendations.append({
                "category": CostCategory.COMPUTE.value,
                "type": "spot_instances",
                "title": "Use Spot Instances for Non-Critical Workloads",
                "description": "Save up to 90% on compute costs for fault-tolerant workloads",
                "potential_savings": 200.00,
                "priority": OptimizationPriority.HIGH.value,
                "effort": "medium",
                "risk": "medium",
            })
            
            recommendations.append({
                "category": CostCategory.COMPUTE.value,
                "type": "auto_scaling",
                "title": "Implement Auto Scaling",
                "description": "Automatically scale instances based on demand",
                "potential_savings": 120.00,
                "priority": OptimizationPriority.MEDIUM.value,
                "effort": "high",
                "risk": "low",
            })
        
        return recommendations
    
    async def _get_storage_optimizations(self, project_id: str, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get storage-specific optimization recommendations."""
        recommendations = []
        
        storage_service = cost_data.get("services", {}).get("storage", {})
        storage_cost = storage_service.get("total_cost", 0)
        
        if storage_cost > 50:
            recommendations.append({
                "category": CostCategory.STORAGE.value,
                "type": "compression",
                "title": "Enable Data Compression",
                "description": "Reduce storage costs by compressing infrequently accessed data",
                "potential_savings": 25.00,
                "priority": OptimizationPriority.MEDIUM.value,
                "effort": "low",
                "risk": "low",
            })
        
        return recommendations
    
    async def _get_database_optimizations(self, project_id: str, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get database-specific optimization recommendations."""
        recommendations = []
        
        db_service = cost_data.get("services", {}).get("database", {})
        db_cost = db_service.get("total_cost", 0)
        
        if db_cost > 150:
            recommendations.append({
                "category": CostCategory.DATABASE.value,
                "type": "read_replicas",
                "title": "Optimize Read Replica Usage",
                "description": "Review and optimize read replica configuration",
                "potential_savings": 50.00,
                "priority": OptimizationPriority.MEDIUM.value,
                "effort": "medium",
                "risk": "low",
            })
        
        return recommendations
    
    async def _get_network_optimizations(self, project_id: str, cost_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get network-specific optimization recommendations."""
        recommendations = []
        
        network_service = cost_data.get("services", {}).get("network", {})
        network_cost = network_service.get("total_cost", 0)
        
        if network_cost > 50:
            recommendations.append({
                "category": CostCategory.NETWORK.value,
                "type": "cdn",
                "title": "Implement CDN for Static Assets",
                "description": "Reduce bandwidth costs by caching static content",
                "potential_savings": 30.00,
                "priority": OptimizationPriority.MEDIUM.value,
                "effort": "medium",
                "risk": "low",
            })
        
        return recommendations
    
    def _calculate_savings_percentage(self, cost_data: Dict[str, Any], potential_savings: float) -> float:
        """Calculate potential savings as percentage of total cost."""
        total_cost = cost_data.get("total_cost", 0)
        if total_cost > 0:
            return round((potential_savings / total_cost) * 100, 2)
        return 0.0
    
    def _get_top_cost_drivers(self, service_breakdown: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get top cost drivers sorted by cost."""
        cost_drivers = []
        
        for service, info in service_breakdown.items():
            cost_drivers.append({
                "service": service,
                "cost": info["cost"],
                "category": info["category"],
            })
        
        # Sort by cost descending
        cost_drivers.sort(key=lambda x: x["cost"], reverse=True)
        
        return cost_drivers[:5]  # Top 5 cost drivers
