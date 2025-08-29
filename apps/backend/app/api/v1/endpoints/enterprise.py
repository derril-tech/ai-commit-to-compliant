"""
Enterprise endpoints for premium features.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.services.kubernetes_service import KubernetesService
from app.services.risk_service import RiskService
from app.services.compliance_service import ComplianceService
from app.services.supply_chain_service import SupplyChainService
from app.services.cost_service import CostService

router = APIRouter()
security = HTTPBearer()

# Initialize services
k8s_service = KubernetesService()
risk_service = RiskService()
compliance_service = ComplianceService()
supply_chain_service = SupplyChainService()
cost_service = CostService()


class KubernetesManifestRequest(BaseModel):
    """Kubernetes manifest generation request."""
    audit_result: Dict[str, Any]
    environment: str = "production"


class ArgoApplicationRequest(BaseModel):
    """ArgoCD application request."""
    git_repo: str
    environment: str = "production"


class RiskAssessmentRequest(BaseModel):
    """Risk assessment request."""
    deployment_context: Dict[str, Any]


class ComplianceAssessmentRequest(BaseModel):
    """Compliance assessment request."""
    frameworks: List[str]


class SLSAProvenanceRequest(BaseModel):
    """SLSA provenance request."""
    build_context: Dict[str, Any]


class BudgetAlertRequest(BaseModel):
    """Budget alert request."""
    budget_amount: float
    currency: str = "USD"
    period: str = "monthly"
    thresholds: List[int] = [50, 80, 100]
    notification_channels: List[str] = ["email"]
    enabled: bool = True


# Kubernetes & GitOps Endpoints
@router.post("/{project_id}/kubernetes/manifests")
async def generate_kubernetes_manifests(
    project_id: str,
    request: KubernetesManifestRequest,
    token: str = Depends(security)
):
    """Generate Kubernetes manifests for project."""
    try:
        manifests = await k8s_service.generate_k8s_manifests(
            project_id, 
            request.audit_result, 
            request.environment
        )
        return manifests
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Kubernetes manifests: {str(e)}")


@router.post("/{project_id}/argocd/application")
async def create_argocd_application(
    project_id: str,
    request: ArgoApplicationRequest,
    token: str = Depends(security)
):
    """Create ArgoCD application for GitOps."""
    try:
        application = await k8s_service.generate_argocd_application(
            project_id,
            request.git_repo,
            request.environment
        )
        return application
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ArgoCD application: {str(e)}")


@router.post("/{project_id}/gitops/pr")
async def create_gitops_pr(
    project_id: str,
    git_repo: str,
    manifests: Dict[str, str],
    environment: str = "production",
    token: str = Depends(security)
):
    """Create GitOps PR with manifests."""
    try:
        pr_result = await k8s_service.create_gitops_pr(
            project_id,
            git_repo,
            manifests,
            environment
        )
        return pr_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create GitOps PR: {str(e)}")


# Risk Assessment Endpoints
@router.post("/{project_id}/risk/assess")
async def assess_deployment_risk(
    project_id: str,
    request: RiskAssessmentRequest,
    token: str = Depends(security)
):
    """Assess deployment risk."""
    try:
        risk_assessment = await risk_service.assess_deployment_risk(
            project_id,
            request.deployment_context
        )
        return risk_assessment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess deployment risk: {str(e)}")


@router.get("/{project_id}/risk/trends")
async def get_risk_trends(
    project_id: str,
    days: int = 30,
    token: str = Depends(security)
):
    """Get risk trends over time."""
    try:
        trends = await risk_service.get_risk_trends(project_id, days)
        return trends
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk trends: {str(e)}")


# Compliance Endpoints
@router.post("/{project_id}/compliance/assess")
async def assess_compliance(
    project_id: str,
    request: ComplianceAssessmentRequest,
    token: str = Depends(security)
):
    """Assess compliance against frameworks."""
    try:
        assessment = await compliance_service.assess_compliance(
            project_id,
            request.frameworks
        )
        return assessment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess compliance: {str(e)}")


@router.get("/{project_id}/compliance/{framework}/pack")
async def generate_compliance_pack(
    project_id: str,
    framework: str,
    token: str = Depends(security)
):
    """Generate compliance pack for framework."""
    try:
        pack = await compliance_service.generate_compliance_pack(project_id, framework)
        return pack
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance pack: {str(e)}")


@router.post("/{project_id}/compliance/{framework}/{control_id}/evidence")
async def collect_evidence(
    project_id: str,
    framework: str,
    control_id: str,
    token: str = Depends(security)
):
    """Collect evidence for compliance control."""
    try:
        evidence = await compliance_service.collect_evidence(project_id, framework, control_id)
        return evidence
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect evidence: {str(e)}")


# Supply Chain Security Endpoints
@router.post("/{project_id}/supply-chain/slsa")
async def generate_slsa_provenance(
    project_id: str,
    request: SLSAProvenanceRequest,
    token: str = Depends(security)
):
    """Generate SLSA provenance attestation."""
    try:
        provenance = await supply_chain_service.generate_slsa_provenance(
            project_id,
            request.build_context
        )
        return provenance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SLSA provenance: {str(e)}")


@router.post("/{project_id}/supply-chain/sign")
async def sign_artifact(
    project_id: str,
    artifact_digest: str,
    artifact_type: str = "container",
    token: str = Depends(security)
):
    """Sign artifact with Sigstore."""
    try:
        signature = await supply_chain_service.sign_artifact(
            project_id,
            artifact_digest,
            artifact_type
        )
        return signature
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sign artifact: {str(e)}")


@router.post("/{project_id}/supply-chain/verify")
async def verify_artifact_signature(
    project_id: str,
    artifact_digest: str,
    signature_data: Dict[str, Any],
    token: str = Depends(security)
):
    """Verify artifact signature."""
    try:
        verification = await supply_chain_service.verify_artifact_signature(
            project_id,
            artifact_digest,
            signature_data
        )
        return verification
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify artifact signature: {str(e)}")


@router.post("/{project_id}/supply-chain/sbom")
async def generate_sbom(
    project_id: str,
    build_context: Dict[str, Any],
    token: str = Depends(security)
):
    """Generate Software Bill of Materials."""
    try:
        sbom = await supply_chain_service.generate_sbom(project_id, build_context)
        return sbom
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SBOM: {str(e)}")


@router.get("/{project_id}/supply-chain/risk")
async def assess_supply_chain_risk(
    project_id: str,
    sbom: Dict[str, Any],
    token: str = Depends(security)
):
    """Assess supply chain security risks."""
    try:
        risk_assessment = await supply_chain_service.assess_supply_chain_risk(project_id, sbom)
        return risk_assessment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess supply chain risk: {str(e)}")


# Cost Optimization Endpoints
@router.get("/{project_id}/cost/analyze")
async def analyze_costs(
    project_id: str,
    time_period: str = "30d",
    token: str = Depends(security)
):
    """Analyze project costs."""
    try:
        analysis = await cost_service.analyze_costs(project_id, time_period)
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze costs: {str(e)}")


@router.get("/{project_id}/cost/recommendations")
async def get_cost_recommendations(
    project_id: str,
    token: str = Depends(security)
):
    """Get cost optimization recommendations."""
    try:
        recommendations = await cost_service.get_optimization_recommendations(project_id)
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost recommendations: {str(e)}")


@router.get("/{project_id}/cost/breakdown")
async def get_cost_breakdown(
    project_id: str,
    time_period: str = "30d",
    token: str = Depends(security)
):
    """Get detailed cost breakdown."""
    try:
        breakdown = await cost_service.get_cost_breakdown(project_id, time_period)
        return breakdown
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost breakdown: {str(e)}")


@router.post("/{project_id}/cost/budget-alert")
async def create_budget_alert(
    project_id: str,
    request: BudgetAlertRequest,
    token: str = Depends(security)
):
    """Create budget alert."""
    try:
        alert = await cost_service.create_budget_alert(
            project_id,
            request.dict()
        )
        return alert
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create budget alert: {str(e)}")


# Combined Enterprise Dashboard
@router.get("/{project_id}/enterprise/dashboard")
async def get_enterprise_dashboard(
    project_id: str,
    token: str = Depends(security)
):
    """Get comprehensive enterprise dashboard."""
    try:
        # Gather data from all enterprise services
        dashboard_data = {
            "project_id": project_id,
            "generated_at": "2024-01-01T00:00:00Z",
        }
        
        # Add risk summary
        try:
            risk_trends = await risk_service.get_risk_trends(project_id, 7)
            dashboard_data["risk_summary"] = {
                "current_risk_level": "medium",
                "trend": risk_trends["statistics"]["trend_direction"],
                "avg_score": risk_trends["statistics"]["avg_risk_score"],
            }
        except Exception:
            dashboard_data["risk_summary"] = {"status": "unavailable"}
        
        # Add compliance summary
        try:
            compliance_assessment = await compliance_service.assess_compliance(project_id, ["soc2"])
            dashboard_data["compliance_summary"] = {
                "overall_score": compliance_assessment["overall_score"],
                "frameworks_assessed": len(compliance_assessment["assessments"]),
            }
        except Exception:
            dashboard_data["compliance_summary"] = {"status": "unavailable"}
        
        # Add cost summary
        try:
            cost_analysis = await cost_service.analyze_costs(project_id, "30d")
            dashboard_data["cost_summary"] = {
                "monthly_cost": cost_analysis["current_costs"]["total_cost"],
                "trend": cost_analysis["trends"]["trend_direction"],
                "optimization_opportunities": len(cost_analysis["optimizations"]),
            }
        except Exception:
            dashboard_data["cost_summary"] = {"status": "unavailable"}
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enterprise dashboard: {str(e)}")
