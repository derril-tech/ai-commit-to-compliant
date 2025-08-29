"""
Plan service for generating deployment blueprints.
"""

from typing import Dict, Any, List
import json
from datetime import datetime

from app.core.config import settings


class PlanService:
    """Service for generating deployment plans and blueprints."""
    
    async def generate_blueprint(self, project_id: str, audit_result: Dict[str, Any], target: str = "vercel") -> Dict[str, Any]:
        """Generate a complete deployment blueprint."""
        
        # Generate IaC templates
        iac_templates = await self._generate_iac_plan(audit_result, target)
        
        # Generate CI/CD templates
        cicd_templates = await self._generate_cicd_plan(audit_result)
        
        # Generate policy configuration
        policies = await self._generate_policy_config(audit_result)
        
        # Calculate cost estimate
        cost_estimate = await self._calculate_cost_estimate(audit_result, target)
        
        # Generate plan diff
        plan_diff = await self._generate_plan_diff(iac_templates, cicd_templates)
        
        return {
            "project_id": project_id,
            "iac_ref": f"s3://{settings.S3_BUCKET}/iac/{project_id}/terraform.zip",
            "cicd_ref": f"s3://{settings.S3_BUCKET}/cicd/{project_id}/workflows.zip",
            "policies": policies,
            "cost_estimate": cost_estimate,
            "plan_diff": plan_diff,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "target": target,
            "audit_summary": {
                "services_detected": len(audit_result.get("services", [])),
                "languages": list(audit_result.get("languages", {}).keys()),
                "frameworks": audit_result.get("frameworks", []),
                "databases": audit_result.get("databases", []),
                "has_docker": audit_result.get("docker", {}).get("dockerfile", False),
                "has_tests": audit_result.get("tests", {}).get("test_files", 0) > 0,
            }
        }
    
    async def _generate_iac_plan(self, audit_result: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Generate Infrastructure as Code plan."""
        databases = audit_result.get("databases", [])
        services = audit_result.get("services", [])
        
        resources = []
        
        # VPC and networking
        resources.extend([
            {"type": "aws_vpc", "name": "main", "estimated_cost_monthly": 0},
            {"type": "aws_internet_gateway", "name": "main", "estimated_cost_monthly": 0},
            {"type": "aws_subnet", "name": "public", "count": 2, "estimated_cost_monthly": 0},
            {"type": "aws_subnet", "name": "private", "count": 2, "estimated_cost_monthly": 0},
        ])
        
        # S3 for artifacts
        resources.append({
            "type": "aws_s3_bucket",
            "name": "artifacts",
            "estimated_cost_monthly": 5.0
        })
        
        # Database resources
        if "postgresql" in databases:
            resources.append({
                "type": "aws_db_instance",
                "name": "postgres",
                "instance_class": "db.t3.micro",
                "estimated_cost_monthly": 15.0
            })
        
        if "redis" in databases:
            resources.append({
                "type": "aws_elasticache_replication_group",
                "name": "redis",
                "node_type": "cache.t3.micro",
                "estimated_cost_monthly": 12.0
            })
        
        # Compute resources based on target
        if target == "vercel":
            resources.append({
                "type": "vercel_project",
                "name": "main",
                "estimated_cost_monthly": 0  # Free tier
            })
        elif target == "render":
            resources.append({
                "type": "render_service",
                "name": "web",
                "estimated_cost_monthly": 7.0  # Starter plan
            })
        elif target == "k8s":
            resources.extend([
                {"type": "aws_eks_cluster", "name": "main", "estimated_cost_monthly": 73.0},
                {"type": "aws_eks_node_group", "name": "workers", "estimated_cost_monthly": 45.0},
            ])
        
        return {
            "resources": resources,
            "total_resources": len(resources),
            "terraform_version": "1.6.6",
            "providers": self._get_required_providers(target),
        }
    
    async def _generate_cicd_plan(self, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CI/CD pipeline plan."""
        languages = audit_result.get("languages", {})
        frameworks = audit_result.get("frameworks", [])
        has_docker = audit_result.get("docker", {}).get("dockerfile", False)
        
        workflows = []
        
        # Main CI/CD workflow
        workflow_steps = [
            {"name": "checkout", "estimated_duration_minutes": 0.5},
            {"name": "setup_environment", "estimated_duration_minutes": 2},
            {"name": "install_dependencies", "estimated_duration_minutes": 3},
            {"name": "lint", "estimated_duration_minutes": 1},
            {"name": "test", "estimated_duration_minutes": 5},
            {"name": "build", "estimated_duration_minutes": 3},
        ]
        
        if has_docker:
            workflow_steps.extend([
                {"name": "docker_build", "estimated_duration_minutes": 4},
                {"name": "security_scan", "estimated_duration_minutes": 2},
                {"name": "sign_image", "estimated_duration_minutes": 1},
            ])
        
        workflow_steps.extend([
            {"name": "deploy_staging", "estimated_duration_minutes": 5},
            {"name": "smoke_tests", "estimated_duration_minutes": 2},
        ])
        
        workflows.append({
            "name": "ci_cd_pipeline",
            "trigger": ["push", "pull_request"],
            "steps": workflow_steps,
            "estimated_total_duration_minutes": sum(step["estimated_duration_minutes"] for step in workflow_steps),
        })
        
        # Security workflow
        workflows.append({
            "name": "security_scan",
            "trigger": ["schedule", "workflow_dispatch"],
            "steps": [
                {"name": "trivy_scan", "estimated_duration_minutes": 3},
                {"name": "codeql_analysis", "estimated_duration_minutes": 10},
                {"name": "dependency_check", "estimated_duration_minutes": 2},
            ],
            "estimated_total_duration_minutes": 15,
        })
        
        return {
            "workflows": workflows,
            "total_workflows": len(workflows),
            "languages_detected": list(languages.keys()),
            "frameworks_detected": frameworks,
            "docker_enabled": has_docker,
        }
    
    async def _generate_policy_config(self, audit_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate policy gate configuration."""
        test_info = audit_result.get("tests", {})
        has_tests = test_info.get("test_files", 0) > 0
        
        policies = [
            {
                "name": "test_coverage",
                "enabled": has_tests,
                "type": "quality_gate",
                "threshold": {
                    "line_coverage": 80 if has_tests else 0,
                    "branch_coverage": 70 if has_tests else 0,
                },
                "waivable": True,
                "description": "Enforce minimum test coverage requirements",
                "remediation_url": "https://docs.prodsprints.ai/policies/test-coverage"
            },
            {
                "name": "security_scan",
                "enabled": True,
                "type": "security_gate",
                "threshold": {
                    "max_critical_vulnerabilities": 0,
                    "max_high_vulnerabilities": 2,
                    "max_medium_vulnerabilities": 10,
                },
                "waivable": True,
                "description": "Block deployments with critical security vulnerabilities",
                "remediation_url": "https://docs.prodsprints.ai/policies/security-scan"
            },
            {
                "name": "performance_budget",
                "enabled": True,
                "type": "performance_gate",
                "threshold": {
                    "p95_response_time_ms": 500,
                    "error_rate_percent": 1.0,
                    "min_requests_per_second": 10,
                },
                "waivable": False,
                "description": "Ensure application meets performance requirements",
                "remediation_url": "https://docs.prodsprints.ai/policies/performance-budget"
            },
            {
                "name": "cost_budget",
                "enabled": True,
                "type": "cost_gate",
                "threshold": {
                    "max_monthly_cost_usd": 100,
                    "max_cost_increase_percent": 20,
                },
                "waivable": True,
                "description": "Prevent unexpected cost increases",
                "remediation_url": "https://docs.prodsprints.ai/policies/cost-budget"
            },
            {
                "name": "compliance_check",
                "enabled": True,
                "type": "compliance_gate",
                "threshold": {
                    "min_compliance_score": 80,
                    "required_checks": ["https_enforced", "auth_required", "input_validation"],
                },
                "waivable": True,
                "description": "Basic security and compliance requirements",
                "remediation_url": "https://docs.prodsprints.ai/policies/compliance"
            }
        ]
        
        return policies
    
    async def _calculate_cost_estimate(self, audit_result: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Calculate monthly cost estimate."""
        databases = audit_result.get("databases", [])
        services = audit_result.get("services", [])
        
        costs = {
            "compute": 0,
            "database": 0,
            "storage": 5.0,  # S3 artifacts
            "networking": 2.0,  # Data transfer
            "monitoring": 0,  # Free tier
        }
        
        # Compute costs based on target
        if target == "vercel":
            costs["compute"] = 0  # Free tier for hobby projects
        elif target == "render":
            costs["compute"] = 7.0  # Starter plan
        elif target == "k8s":
            costs["compute"] = 73.0 + 45.0  # EKS cluster + node group
        
        # Database costs
        if "postgresql" in databases:
            costs["database"] += 15.0  # RDS t3.micro
        if "redis" in databases:
            costs["database"] += 12.0  # ElastiCache t3.micro
        if "mongodb" in databases:
            costs["database"] += 20.0  # DocumentDB
        
        # Additional services
        if len(services) > 2:
            costs["compute"] *= 1.5  # Scale up for multiple services
        
        total_monthly = sum(costs.values())
        
        return {
            "monthly_estimate": round(total_monthly, 2),
            "breakdown": costs,
            "currency": "USD",
            "confidence": "medium",
            "factors": [
                "Estimates based on AWS pricing in us-east-1",
                "Assumes development/staging workloads",
                "Production costs may be 2-3x higher",
                "Costs exclude data transfer and premium support",
            ],
            "cost_optimization_tips": [
                "Use spot instances for non-critical workloads",
                "Enable auto-scaling to optimize resource usage",
                "Consider reserved instances for predictable workloads",
                "Monitor and right-size resources regularly",
            ]
        }
    
    async def _generate_plan_diff(self, iac_templates: Dict[str, Any], cicd_templates: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plan diff preview."""
        resources = iac_templates.get("resources", [])
        workflows = cicd_templates.get("workflows", [])
        
        return {
            "resources_to_create": len(resources),
            "resources_to_modify": 0,
            "resources_to_destroy": 0,
            "workflows_to_create": len(workflows),
            "estimated_apply_time_minutes": 15,
            "preview": f"Will create {len(resources)} infrastructure resources and {len(workflows)} CI/CD workflows",
            "changes": [
                {
                    "type": "create",
                    "resource_type": "aws_vpc",
                    "resource_name": "main",
                    "description": "VPC for application infrastructure"
                },
                {
                    "type": "create",
                    "resource_type": "aws_s3_bucket",
                    "resource_name": "artifacts",
                    "description": "S3 bucket for build artifacts and logs"
                },
                {
                    "type": "create",
                    "resource_type": "github_workflow",
                    "resource_name": "ci_cd_pipeline",
                    "description": "Main CI/CD pipeline workflow"
                }
            ],
            "warnings": [],
            "blockers": []
        }
    
    def _get_required_providers(self, target: str) -> List[Dict[str, str]]:
        """Get required Terraform providers."""
        providers = [
            {"name": "aws", "version": "~> 5.0"},
            {"name": "random", "version": "~> 3.4"},
        ]
        
        if target == "vercel":
            providers.append({"name": "vercel", "version": "~> 0.15"})
        elif target == "k8s":
            providers.extend([
                {"name": "kubernetes", "version": "~> 2.23"},
                {"name": "helm", "version": "~> 2.11"},
            ])
        
        return providers
