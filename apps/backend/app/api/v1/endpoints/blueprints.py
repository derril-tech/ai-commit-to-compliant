"""
Blueprint/plan generation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any, List

from app.services.plan_service import PlanService

router = APIRouter()
security = HTTPBearer()
plan_service = PlanService()


class BlueprintGenerateRequest(BaseModel):
    """Blueprint generation request."""
    project_id: str
    force_regenerate: bool = False
    target: str = "vercel"


class PolicyGate(BaseModel):
    """Policy gate configuration."""
    name: str
    enabled: bool
    threshold: Dict[str, Any]
    waivable: bool = True
    description: str
    remediation_url: str = None


class CostEstimate(BaseModel):
    """Cost estimation."""
    monthly_estimate: float
    breakdown: Dict[str, float]
    currency: str = "USD"
    confidence: str = "medium"
    factors: List[str]
    cost_optimization_tips: List[str]


class BlueprintResponse(BaseModel):
    """Blueprint response model."""
    project_id: str
    iac_ref: str
    cicd_ref: str
    policies: List[PolicyGate]
    cost_estimate: CostEstimate
    plan_diff: Dict[str, Any]
    created_at: str
    target: str
    audit_summary: Dict[str, Any]


@router.post("/generate", response_model=BlueprintResponse)
async def generate_blueprint(
    request: BlueprintGenerateRequest,
    token: str = Depends(security)
):
    """Generate IaC + CI/CD + policies + cost plan."""
    try:
        # Mock audit result for now - in real implementation this would come from database
        mock_audit_result = {
            "services": [
                {"name": "frontend", "type": "nodejs", "path": ".", "config_file": "package.json"},
                {"name": "api", "type": "python", "path": "api", "config_file": "requirements.txt"}
            ],
            "frameworks": ["Next.js", "FastAPI"],
            "languages": {"TypeScript": 45, "Python": 32, "JavaScript": 8},
            "databases": ["postgresql", "redis"],
            "docker": {"dockerfile": True, "docker_compose": True},
            "tests": {"test_files": 23, "test_frameworks": ["jest", "pytest"], "coverage_config": True},
            "ci_cd": {"github_actions": True},
            "env_vars": ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"],
            "migrations": {"has_migrations": True, "migration_tool": "alembic", "migration_count": 5},
            "ports": [3000, 8000],
            "dependencies": {"package_managers": ["npm", "pip"], "dependency_count": 67}
        }
        
        blueprint = await plan_service.generate_blueprint(
            request.project_id, 
            mock_audit_result, 
            request.target
        )
        
        return blueprint
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate blueprint: {str(e)}")


@router.get("/{project_id}", response_model=BlueprintResponse)
async def get_blueprint(
    project_id: str,
    token: str = Depends(security)
):
    """Get latest blueprint for project."""
    try:
        # Mock audit result for retrieval - in real implementation this would come from database
        mock_audit_result = {
            "services": [
                {"name": "frontend", "type": "nodejs", "path": ".", "config_file": "package.json"},
                {"name": "api", "type": "python", "path": "api", "config_file": "requirements.txt"}
            ],
            "frameworks": ["Next.js", "FastAPI"],
            "languages": {"TypeScript": 45, "Python": 32, "JavaScript": 8},
            "databases": ["postgresql", "redis"],
            "docker": {"dockerfile": True, "docker_compose": True},
            "tests": {"test_files": 23, "test_frameworks": ["jest", "pytest"], "coverage_config": True},
            "ci_cd": {"github_actions": True},
            "env_vars": ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"],
            "migrations": {"has_migrations": True, "migration_tool": "alembic", "migration_count": 5},
            "ports": [3000, 8000],
            "dependencies": {"package_managers": ["npm", "pip"], "dependency_count": 67}
        }
        
        blueprint = await plan_service.generate_blueprint(project_id, mock_audit_result, "vercel")
        return blueprint
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve blueprint: {str(e)}")
