"""
Risk assessment service with ML-based deployment risk scoring.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import math

from app.core.config import settings


class RiskLevel(Enum):
    """Risk levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    """Risk categories."""
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    BUSINESS = "business"


class RiskService:
    """Service for deployment risk assessment and scoring."""
    
    async def assess_deployment_risk(self, project_id: str, deployment_context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive deployment risk assessment."""
        try:
            risk_factors = []
            
            # Technical risk factors
            technical_risks = await self._assess_technical_risks(project_id, deployment_context)
            risk_factors.extend(technical_risks)
            
            # Operational risk factors
            operational_risks = await self._assess_operational_risks(project_id, deployment_context)
            risk_factors.extend(operational_risks)
            
            # Security risk factors
            security_risks = await self._assess_security_risks(project_id, deployment_context)
            risk_factors.extend(security_risks)
            
            # Compliance risk factors
            compliance_risks = await self._assess_compliance_risks(project_id, deployment_context)
            risk_factors.extend(compliance_risks)
            
            # Business risk factors
            business_risks = await self._assess_business_risks(project_id, deployment_context)
            risk_factors.extend(business_risks)
            
            # Calculate overall risk score
            overall_score = await self._calculate_risk_score(risk_factors)
            risk_level = self._determine_risk_level(overall_score)
            
            # Generate recommendations
            recommendations = await self._generate_risk_recommendations(risk_factors, risk_level)
            
            # Calculate deployment confidence
            confidence_score = await self._calculate_deployment_confidence(project_id, risk_factors)
            
            return {
                "project_id": project_id,
                "assessment_id": f"risk-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "overall_risk_score": overall_score,
                "risk_level": risk_level.value,
                "confidence_score": confidence_score,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "suggested_strategy": self._suggest_deployment_strategy(risk_level, confidence_score),
                "mitigation_actions": await self._generate_mitigation_actions(risk_factors),
                "assessment_timestamp": datetime.utcnow().isoformat() + "Z",
                "valid_until": (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to assess deployment risk: {str(e)}")
    
    async def get_risk_trends(self, project_id: str, days: int = 30) -> Dict[str, Any]:
        """Get risk trends over time."""
        try:
            # TODO: Query historical risk data
            # For now, generate sample trend data
            
            dates = []
            risk_scores = []
            confidence_scores = []
            
            for i in range(days):
                date = datetime.utcnow() - timedelta(days=days-i-1)
                dates.append(date.isoformat()[:10])
                
                # Simulate trending data
                base_risk = 3.5 + math.sin(i * 0.1) * 0.5
                risk_scores.append(round(base_risk + (i % 7) * 0.1, 2))
                
                base_confidence = 85 + math.cos(i * 0.15) * 5
                confidence_scores.append(round(base_confidence + (i % 5) * 2, 1))
            
            return {
                "project_id": project_id,
                "time_period_days": days,
                "trends": {
                    "dates": dates,
                    "risk_scores": risk_scores,
                    "confidence_scores": confidence_scores,
                },
                "statistics": {
                    "avg_risk_score": sum(risk_scores) / len(risk_scores),
                    "max_risk_score": max(risk_scores),
                    "min_risk_score": min(risk_scores),
                    "avg_confidence": sum(confidence_scores) / len(confidence_scores),
                    "trend_direction": "stable",  # Could be "increasing", "decreasing", "stable"
                },
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to get risk trends: {str(e)}")
    
    async def _assess_technical_risks(self, project_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess technical risk factors."""
        risks = []
        
        # Code quality risks
        test_coverage = context.get("test_coverage", 80)
        if test_coverage < 70:
            risks.append({
                "category": RiskCategory.TECHNICAL.value,
                "factor": "low_test_coverage",
                "score": 8.0,
                "weight": 0.8,
                "description": f"Test coverage is {test_coverage}%, below recommended 80%",
                "impact": "high",
                "likelihood": "medium",
            })
        elif test_coverage < 80:
            risks.append({
                "category": RiskCategory.TECHNICAL.value,
                "factor": "moderate_test_coverage",
                "score": 5.0,
                "weight": 0.6,
                "description": f"Test coverage is {test_coverage}%, below optimal 80%",
                "impact": "medium",
                "likelihood": "low",
            })
        
        # Dependency risks
        outdated_deps = context.get("outdated_dependencies", 5)
        if outdated_deps > 10:
            risks.append({
                "category": RiskCategory.TECHNICAL.value,
                "factor": "outdated_dependencies",
                "score": 7.0,
                "weight": 0.7,
                "description": f"{outdated_deps} outdated dependencies detected",
                "impact": "medium",
                "likelihood": "medium",
            })
        
        # Performance risks
        performance_score = context.get("performance_score", 85)
        if performance_score < 70:
            risks.append({
                "category": RiskCategory.TECHNICAL.value,
                "factor": "poor_performance",
                "score": 8.5,
                "weight": 0.9,
                "description": f"Performance score is {performance_score}%, indicating potential issues",
                "impact": "high",
                "likelihood": "high",
            })
        
        # Database migration risks
        has_migrations = context.get("has_database_migrations", False)
        if has_migrations:
            migration_complexity = context.get("migration_complexity", "low")
            if migration_complexity == "high":
                risks.append({
                    "category": RiskCategory.TECHNICAL.value,
                    "factor": "complex_database_migration",
                    "score": 9.0,
                    "weight": 0.9,
                    "description": "Complex database migrations increase deployment risk",
                    "impact": "high",
                    "likelihood": "medium",
                })
        
        return risks
    
    async def _assess_operational_risks(self, project_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess operational risk factors."""
        risks = []
        
        # Deployment timing risks
        now = datetime.utcnow()
        hour = now.hour
        day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday
        
        if 9 <= hour <= 17 and day_of_week < 5:  # Business hours on weekdays
            risks.append({
                "category": RiskCategory.OPERATIONAL.value,
                "factor": "business_hours_deployment",
                "score": 6.0,
                "weight": 0.5,
                "description": "Deploying during business hours increases user impact risk",
                "impact": "medium",
                "likelihood": "high",
            })
        
        if day_of_week == 4:  # Friday
            risks.append({
                "category": RiskCategory.OPERATIONAL.value,
                "factor": "friday_deployment",
                "score": 7.0,
                "weight": 0.6,
                "description": "Friday deployments have higher risk due to limited weekend support",
                "impact": "medium",
                "likelihood": "medium",
            })
        
        # Team availability risks
        team_size = context.get("team_size", 3)
        if team_size < 2:
            risks.append({
                "category": RiskCategory.OPERATIONAL.value,
                "factor": "small_team_size",
                "score": 6.5,
                "weight": 0.7,
                "description": f"Small team size ({team_size}) limits incident response capability",
                "impact": "medium",
                "likelihood": "medium",
            })
        
        # Monitoring and alerting risks
        monitoring_coverage = context.get("monitoring_coverage", 90)
        if monitoring_coverage < 80:
            risks.append({
                "category": RiskCategory.OPERATIONAL.value,
                "factor": "insufficient_monitoring",
                "score": 8.0,
                "weight": 0.8,
                "description": f"Monitoring coverage is {monitoring_coverage}%, below recommended 90%",
                "impact": "high",
                "likelihood": "medium",
            })
        
        # Rollback capability risks
        rollback_tested = context.get("rollback_tested", False)
        if not rollback_tested:
            risks.append({
                "category": RiskCategory.OPERATIONAL.value,
                "factor": "untested_rollback",
                "score": 7.5,
                "weight": 0.8,
                "description": "Rollback procedure has not been tested recently",
                "impact": "high",
                "likelihood": "low",
            })
        
        return risks
    
    async def _assess_security_risks(self, project_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess security risk factors."""
        risks = []
        
        # Vulnerability risks
        critical_vulns = context.get("critical_vulnerabilities", 0)
        high_vulns = context.get("high_vulnerabilities", 0)
        
        if critical_vulns > 0:
            risks.append({
                "category": RiskCategory.SECURITY.value,
                "factor": "critical_vulnerabilities",
                "score": 9.5,
                "weight": 1.0,
                "description": f"{critical_vulns} critical security vulnerabilities found",
                "impact": "critical",
                "likelihood": "high",
            })
        
        if high_vulns > 3:
            risks.append({
                "category": RiskCategory.SECURITY.value,
                "factor": "high_vulnerabilities",
                "score": 7.5,
                "weight": 0.8,
                "description": f"{high_vulns} high-severity vulnerabilities found",
                "impact": "high",
                "likelihood": "medium",
            })
        
        # Secrets management risks
        secrets_encrypted = context.get("secrets_encrypted", True)
        if not secrets_encrypted:
            risks.append({
                "category": RiskCategory.SECURITY.value,
                "factor": "unencrypted_secrets",
                "score": 9.0,
                "weight": 0.9,
                "description": "Secrets are not properly encrypted",
                "impact": "critical",
                "likelihood": "high",
            })
        
        # Authentication risks
        auth_configured = context.get("authentication_configured", True)
        if not auth_configured:
            risks.append({
                "category": RiskCategory.SECURITY.value,
                "factor": "missing_authentication",
                "score": 8.5,
                "weight": 0.9,
                "description": "Authentication is not properly configured",
                "impact": "high",
                "likelihood": "high",
            })
        
        return risks
    
    async def _assess_compliance_risks(self, project_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess compliance risk factors."""
        risks = []
        
        # Regulatory compliance
        compliance_frameworks = context.get("compliance_frameworks", [])
        
        if "SOC2" in compliance_frameworks:
            soc2_score = context.get("soc2_compliance_score", 95)
            if soc2_score < 90:
                risks.append({
                    "category": RiskCategory.COMPLIANCE.value,
                    "factor": "soc2_compliance_gap",
                    "score": 7.0,
                    "weight": 0.8,
                    "description": f"SOC2 compliance score is {soc2_score}%, below required 90%",
                    "impact": "high",
                    "likelihood": "medium",
                })
        
        if "HIPAA" in compliance_frameworks:
            hipaa_score = context.get("hipaa_compliance_score", 95)
            if hipaa_score < 95:
                risks.append({
                    "category": RiskCategory.COMPLIANCE.value,
                    "factor": "hipaa_compliance_gap",
                    "score": 8.5,
                    "weight": 0.9,
                    "description": f"HIPAA compliance score is {hipaa_score}%, below required 95%",
                    "impact": "critical",
                    "likelihood": "medium",
                })
        
        # Data handling risks
        handles_pii = context.get("handles_pii", False)
        if handles_pii:
            pii_protection_score = context.get("pii_protection_score", 90)
            if pii_protection_score < 85:
                risks.append({
                    "category": RiskCategory.COMPLIANCE.value,
                    "factor": "inadequate_pii_protection",
                    "score": 8.0,
                    "weight": 0.9,
                    "description": f"PII protection score is {pii_protection_score}%, below required 85%",
                    "impact": "high",
                    "likelihood": "medium",
                })
        
        return risks
    
    async def _assess_business_risks(self, project_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess business risk factors."""
        risks = []
        
        # User impact risks
        user_count = context.get("active_users", 1000)
        if user_count > 10000:
            risks.append({
                "category": RiskCategory.BUSINESS.value,
                "factor": "high_user_impact",
                "score": 7.0,
                "weight": 0.8,
                "description": f"High user count ({user_count:,}) increases impact of deployment issues",
                "impact": "high",
                "likelihood": "low",
            })
        
        # Revenue impact risks
        revenue_impact = context.get("revenue_impact", "low")
        if revenue_impact == "high":
            risks.append({
                "category": RiskCategory.BUSINESS.value,
                "factor": "high_revenue_impact",
                "score": 8.5,
                "weight": 0.9,
                "description": "Deployment affects high-revenue generating features",
                "impact": "critical",
                "likelihood": "low",
            })
        elif revenue_impact == "medium":
            risks.append({
                "category": RiskCategory.BUSINESS.value,
                "factor": "medium_revenue_impact",
                "score": 6.0,
                "weight": 0.7,
                "description": "Deployment affects revenue-generating features",
                "impact": "medium",
                "likelihood": "low",
            })
        
        # SLA risks
        sla_requirements = context.get("sla_requirements", {})
        if sla_requirements.get("uptime", 99.0) > 99.9:
            risks.append({
                "category": RiskCategory.BUSINESS.value,
                "factor": "strict_sla_requirements",
                "score": 6.5,
                "weight": 0.7,
                "description": f"Strict SLA requirements ({sla_requirements['uptime']}% uptime) increase deployment pressure",
                "impact": "medium",
                "likelihood": "medium",
            })
        
        return risks
    
    async def _calculate_risk_score(self, risk_factors: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score using weighted average."""
        if not risk_factors:
            return 1.0  # Very low risk if no factors identified
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for factor in risk_factors:
            score = factor.get("score", 5.0)
            weight = factor.get("weight", 1.0)
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 1.0
        
        # Normalize to 1-10 scale
        raw_score = total_weighted_score / total_weight
        return round(min(10.0, max(1.0, raw_score)), 2)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from score."""
        if risk_score >= 8.5:
            return RiskLevel.CRITICAL
        elif risk_score >= 7.0:
            return RiskLevel.HIGH
        elif risk_score >= 5.0:
            return RiskLevel.MEDIUM
        elif risk_score >= 3.0:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    async def _calculate_deployment_confidence(self, project_id: str, risk_factors: List[Dict[str, Any]]) -> float:
        """Calculate deployment confidence score."""
        # Base confidence starts at 100%
        confidence = 100.0
        
        # Reduce confidence based on risk factors
        for factor in risk_factors:
            impact = factor.get("impact", "medium")
            likelihood = factor.get("likelihood", "medium")
            
            # Impact multipliers
            impact_multiplier = {
                "critical": 0.8,
                "high": 0.6,
                "medium": 0.4,
                "low": 0.2,
            }.get(impact, 0.4)
            
            # Likelihood multipliers
            likelihood_multiplier = {
                "high": 1.0,
                "medium": 0.7,
                "low": 0.4,
            }.get(likelihood, 0.7)
            
            # Reduce confidence
            reduction = impact_multiplier * likelihood_multiplier * 10
            confidence -= reduction
        
        return round(max(0.0, min(100.0, confidence)), 1)
    
    async def _generate_risk_recommendations(self, risk_factors: List[Dict[str, Any]], risk_level: RiskLevel) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommendations.append("Consider postponing deployment until critical risks are addressed")
            recommendations.append("Use canary deployment strategy to minimize impact")
            recommendations.append("Ensure rollback procedures are tested and ready")
            recommendations.append("Have incident response team on standby")
        
        # Category-specific recommendations
        categories = set(factor.get("category") for factor in risk_factors)
        
        if RiskCategory.TECHNICAL.value in categories:
            recommendations.append("Increase test coverage before deployment")
            recommendations.append("Update outdated dependencies")
            recommendations.append("Run performance tests to validate changes")
        
        if RiskCategory.SECURITY.value in categories:
            recommendations.append("Address all critical and high-severity vulnerabilities")
            recommendations.append("Verify secrets are properly encrypted")
            recommendations.append("Run security scans before deployment")
        
        if RiskCategory.OPERATIONAL.value in categories:
            recommendations.append("Schedule deployment during low-traffic hours")
            recommendations.append("Ensure monitoring and alerting are comprehensive")
            recommendations.append("Verify team availability for incident response")
        
        if RiskCategory.COMPLIANCE.value in categories:
            recommendations.append("Complete compliance gap analysis")
            recommendations.append("Ensure all regulatory requirements are met")
            recommendations.append("Document compliance evidence")
        
        if RiskCategory.BUSINESS.value in categories:
            recommendations.append("Notify stakeholders of deployment schedule")
            recommendations.append("Prepare communication plan for potential issues")
            recommendations.append("Consider deployment during maintenance window")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _suggest_deployment_strategy(self, risk_level: RiskLevel, confidence_score: float) -> str:
        """Suggest deployment strategy based on risk assessment."""
        if risk_level == RiskLevel.CRITICAL or confidence_score < 60:
            return "canary"  # Most conservative
        elif risk_level == RiskLevel.HIGH or confidence_score < 75:
            return "blue-green"  # Conservative with quick rollback
        elif risk_level == RiskLevel.MEDIUM or confidence_score < 85:
            return "rolling"  # Balanced approach
        else:
            return "direct"  # Fastest for low-risk deployments
    
    async def _generate_mitigation_actions(self, risk_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific mitigation actions for risk factors."""
        actions = []
        
        for factor in risk_factors:
            factor_type = factor.get("factor")
            category = factor.get("category")
            
            if factor_type == "low_test_coverage":
                actions.append({
                    "action": "increase_test_coverage",
                    "title": "Increase Test Coverage",
                    "description": "Add unit and integration tests to reach 80% coverage",
                    "priority": "high",
                    "estimated_effort_hours": 8,
                    "category": category,
                })
            
            elif factor_type == "critical_vulnerabilities":
                actions.append({
                    "action": "fix_vulnerabilities",
                    "title": "Fix Critical Vulnerabilities",
                    "description": "Update dependencies and patch critical security vulnerabilities",
                    "priority": "critical",
                    "estimated_effort_hours": 4,
                    "category": category,
                })
            
            elif factor_type == "insufficient_monitoring":
                actions.append({
                    "action": "improve_monitoring",
                    "title": "Improve Monitoring Coverage",
                    "description": "Add monitoring for key application metrics and health checks",
                    "priority": "medium",
                    "estimated_effort_hours": 6,
                    "category": category,
                })
            
            elif factor_type == "untested_rollback":
                actions.append({
                    "action": "test_rollback",
                    "title": "Test Rollback Procedure",
                    "description": "Verify rollback procedures work correctly in staging environment",
                    "priority": "high",
                    "estimated_effort_hours": 2,
                    "category": category,
                })
        
        return actions
