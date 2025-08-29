"""
Readiness service for managing deployment readiness gates and checks.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.core.config import settings


class ReadinessStatus(Enum):
    """Readiness check status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WAIVED = "waived"
    SKIPPED = "skipped"


class ReadinessService:
    """Service for managing deployment readiness gates."""
    
    async def run_readiness_checks(self, project_id: str, environment: str = "staging") -> Dict[str, Any]:
        """Run all readiness checks for a project."""
        try:
            readiness_id = f"readiness-{project_id}-{environment}-001"
            
            # Initialize readiness run
            readiness_run = {
                "readiness_id": readiness_id,
                "project_id": project_id,
                "environment": environment,
                "status": "running",
                "started_at": datetime.utcnow().isoformat() + "Z",
                "checks": [],
                "overall_score": 0,
                "blockers": [],
            }
            
            # Run all readiness checks in parallel
            check_tasks = [
                self._run_test_coverage_check(project_id),
                self._run_security_check(project_id),
                self._run_performance_check(project_id),
                self._run_infrastructure_check(project_id),
                self._run_compliance_check(project_id),
                self._run_dependency_check(project_id),
                self._run_configuration_check(project_id),
                self._run_monitoring_check(project_id),
            ]
            
            check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
            
            # Process check results
            passed_checks = 0
            total_checks = len(check_results)
            blockers = []
            
            for i, result in enumerate(check_results):
                if isinstance(result, Exception):
                    check = {
                        "name": f"check_{i}",
                        "status": ReadinessStatus.FAILED.value,
                        "message": f"Check failed: {str(result)}",
                        "category": "system",
                        "severity": "high",
                        "waivable": True,
                    }
                else:
                    check = result
                    if check["status"] == ReadinessStatus.PASSED.value:
                        passed_checks += 1
                    elif check["status"] == ReadinessStatus.FAILED.value and not check.get("waivable", True):
                        blockers.append(check["message"])
                
                readiness_run["checks"].append(check)
            
            # Calculate overall score and status
            readiness_run["overall_score"] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
            readiness_run["blockers"] = blockers
            
            if len(blockers) > 0:
                readiness_run["status"] = "blocked"
                readiness_run["overall_status"] = "blocked"
            elif readiness_run["overall_score"] >= 80:
                readiness_run["status"] = "ready"
                readiness_run["overall_status"] = "ready"
            else:
                readiness_run["status"] = "pending"
                readiness_run["overall_status"] = "pending"
            
            readiness_run["completed_at"] = datetime.utcnow().isoformat() + "Z"
            
            return readiness_run
            
        except Exception as e:
            return {
                "readiness_id": f"readiness-{project_id}-error",
                "project_id": project_id,
                "status": "error",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat() + "Z",
            }
    
    async def get_readiness_status(self, project_id: str, environment: str = "staging") -> Dict[str, Any]:
        """Get current readiness status for a project."""
        # TODO: Retrieve from database
        # For now, return mock data
        return {
            "project_id": project_id,
            "environment": environment,
            "overall_status": "ready",
            "overall_score": 85.5,
            "last_check": "2024-01-01T00:00:00Z",
            "checks_summary": {
                "total": 8,
                "passed": 7,
                "failed": 1,
                "waived": 0,
                "pending": 0,
            },
            "blockers": [],
            "recommendations": [
                "Consider increasing test coverage to 90%",
                "Update 2 dependencies with known vulnerabilities",
            ],
        }
    
    async def waive_readiness_check(self, project_id: str, check_name: str, reason: str, waived_by: str) -> Dict[str, Any]:
        """Waive a failed readiness check."""
        try:
            waiver = {
                "project_id": project_id,
                "check_name": check_name,
                "reason": reason,
                "waived_by": waived_by,
                "waived_at": datetime.utcnow().isoformat() + "Z",
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
                "waiver_id": f"waiver-{project_id}-{check_name}-001",
            }
            
            # TODO: Store waiver in database
            # TODO: Update readiness status
            
            return waiver
            
        except Exception as e:
            raise Exception(f"Failed to waive readiness check: {str(e)}")
    
    async def _run_test_coverage_check(self, project_id: str) -> Dict[str, Any]:
        """Run test coverage readiness check."""
        try:
            # TODO: Integrate with actual test coverage data
            # For now, simulate check
            
            coverage_data = {
                "line_coverage": 82.5,
                "branch_coverage": 75.3,
                "function_coverage": 88.1,
                "statement_coverage": 81.7,
            }
            
            threshold = 80.0
            passed = coverage_data["line_coverage"] >= threshold
            
            return {
                "name": "test_coverage",
                "category": "quality",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": f"Line coverage: {coverage_data['line_coverage']}% (threshold: {threshold}%)",
                "details": coverage_data,
                "severity": "medium" if not passed else "info",
                "waivable": True,
                "remediation_url": "https://docs.prodsprints.ai/readiness/test-coverage",
                "estimated_fix_time_minutes": 60 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "test_coverage",
                "category": "quality",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Test coverage check failed: {str(e)}",
                "severity": "high",
                "waivable": True,
            }
    
    async def _run_security_check(self, project_id: str) -> Dict[str, Any]:
        """Run security readiness check."""
        try:
            # TODO: Integrate with actual security scan results
            # For now, simulate check
            
            security_issues = {
                "critical": 0,
                "high": 1,
                "medium": 3,
                "low": 5,
                "total": 9,
            }
            
            # Check against thresholds
            critical_threshold = 0
            high_threshold = 2
            
            passed = (security_issues["critical"] <= critical_threshold and 
                     security_issues["high"] <= high_threshold)
            
            message = f"Security scan: {security_issues['critical']} critical, {security_issues['high']} high vulnerabilities"
            
            return {
                "name": "security_scan",
                "category": "security",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": message,
                "details": security_issues,
                "severity": "high" if not passed else "info",
                "waivable": True,
                "remediation_url": "https://docs.prodsprints.ai/readiness/security",
                "estimated_fix_time_minutes": 120 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "security_scan",
                "category": "security",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Security check failed: {str(e)}",
                "severity": "high",
                "waivable": True,
            }
    
    async def _run_performance_check(self, project_id: str) -> Dict[str, Any]:
        """Run performance readiness check."""
        try:
            # TODO: Integrate with actual performance test results
            # For now, simulate check
            
            performance_metrics = {
                "p95_response_time_ms": 245,
                "error_rate_percent": 0.12,
                "requests_per_second": 167.5,
                "availability_percent": 99.95,
            }
            
            # Check against thresholds
            p95_threshold = 500
            error_rate_threshold = 1.0
            
            passed = (performance_metrics["p95_response_time_ms"] <= p95_threshold and
                     performance_metrics["error_rate_percent"] <= error_rate_threshold)
            
            message = f"Performance: {performance_metrics['p95_response_time_ms']}ms p95, {performance_metrics['error_rate_percent']}% errors"
            
            return {
                "name": "performance_budget",
                "category": "performance",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": message,
                "details": performance_metrics,
                "severity": "medium" if not passed else "info",
                "waivable": False,  # Performance is critical
                "remediation_url": "https://docs.prodsprints.ai/readiness/performance",
                "estimated_fix_time_minutes": 180 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "performance_budget",
                "category": "performance",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Performance check failed: {str(e)}",
                "severity": "high",
                "waivable": False,
            }
    
    async def _run_infrastructure_check(self, project_id: str) -> Dict[str, Any]:
        """Run infrastructure readiness check."""
        try:
            # TODO: Integrate with actual infrastructure status
            # For now, simulate check
            
            infrastructure_status = {
                "vpc_healthy": True,
                "database_healthy": True,
                "cache_healthy": True,
                "storage_healthy": True,
                "dns_healthy": True,
                "ssl_valid": True,
            }
            
            failed_components = [k for k, v in infrastructure_status.items() if not v]
            passed = len(failed_components) == 0
            
            if passed:
                message = "All infrastructure components are healthy"
            else:
                message = f"Infrastructure issues: {', '.join(failed_components)}"
            
            return {
                "name": "infrastructure_health",
                "category": "infrastructure",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": message,
                "details": infrastructure_status,
                "severity": "high" if not passed else "info",
                "waivable": False,  # Infrastructure is critical
                "remediation_url": "https://docs.prodsprints.ai/readiness/infrastructure",
                "estimated_fix_time_minutes": 30 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "infrastructure_health",
                "category": "infrastructure",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Infrastructure check failed: {str(e)}",
                "severity": "high",
                "waivable": False,
            }
    
    async def _run_compliance_check(self, project_id: str) -> Dict[str, Any]:
        """Run compliance readiness check."""
        try:
            # TODO: Integrate with actual compliance scan results
            # For now, simulate check
            
            compliance_checks = {
                "https_enforced": True,
                "auth_required": True,
                "input_validation": False,
                "error_handling": True,
                "logging_configured": True,
                "secrets_encrypted": True,
            }
            
            failed_checks = [k for k, v in compliance_checks.items() if not v]
            passed = len(failed_checks) == 0
            
            if passed:
                message = "All compliance checks passed"
            else:
                message = f"Compliance issues: {', '.join(failed_checks)}"
            
            return {
                "name": "compliance_check",
                "category": "compliance",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": message,
                "details": compliance_checks,
                "severity": "medium" if not passed else "info",
                "waivable": True,
                "remediation_url": "https://docs.prodsprints.ai/readiness/compliance",
                "estimated_fix_time_minutes": 90 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "compliance_check",
                "category": "compliance",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Compliance check failed: {str(e)}",
                "severity": "medium",
                "waivable": True,
            }
    
    async def _run_dependency_check(self, project_id: str) -> Dict[str, Any]:
        """Run dependency readiness check."""
        try:
            # TODO: Integrate with actual dependency scan results
            # For now, simulate check
            
            dependency_status = {
                "total_dependencies": 127,
                "outdated_dependencies": 8,
                "vulnerable_dependencies": 2,
                "license_violations": 0,
            }
            
            # Check thresholds
            vulnerable_threshold = 5
            passed = dependency_status["vulnerable_dependencies"] <= vulnerable_threshold
            
            message = f"Dependencies: {dependency_status['vulnerable_dependencies']} vulnerable, {dependency_status['outdated_dependencies']} outdated"
            
            return {
                "name": "dependency_check",
                "category": "security",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": message,
                "details": dependency_status,
                "severity": "medium" if not passed else "info",
                "waivable": True,
                "remediation_url": "https://docs.prodsprints.ai/readiness/dependencies",
                "estimated_fix_time_minutes": 45 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "dependency_check",
                "category": "security",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Dependency check failed: {str(e)}",
                "severity": "medium",
                "waivable": True,
            }
    
    async def _run_configuration_check(self, project_id: str) -> Dict[str, Any]:
        """Run configuration readiness check."""
        try:
            # TODO: Integrate with actual configuration validation
            # For now, simulate check
            
            config_status = {
                "environment_variables_set": True,
                "secrets_configured": True,
                "database_migrations_applied": True,
                "feature_flags_configured": True,
                "monitoring_configured": False,
            }
            
            failed_configs = [k for k, v in config_status.items() if not v]
            passed = len(failed_configs) == 0
            
            if passed:
                message = "All configuration checks passed"
            else:
                message = f"Configuration issues: {', '.join(failed_configs)}"
            
            return {
                "name": "configuration_check",
                "category": "configuration",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": message,
                "details": config_status,
                "severity": "medium" if not passed else "info",
                "waivable": True,
                "remediation_url": "https://docs.prodsprints.ai/readiness/configuration",
                "estimated_fix_time_minutes": 30 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "configuration_check",
                "category": "configuration",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Configuration check failed: {str(e)}",
                "severity": "medium",
                "waivable": True,
            }
    
    async def _run_monitoring_check(self, project_id: str) -> Dict[str, Any]:
        """Run monitoring readiness check."""
        try:
            # TODO: Integrate with actual monitoring setup
            # For now, simulate check
            
            monitoring_status = {
                "health_checks_configured": True,
                "metrics_collection_enabled": True,
                "alerting_configured": True,
                "log_aggregation_enabled": True,
                "dashboards_created": False,
            }
            
            failed_monitoring = [k for k, v in monitoring_status.items() if not v]
            passed = len(failed_monitoring) == 0
            
            if passed:
                message = "All monitoring checks passed"
            else:
                message = f"Monitoring issues: {', '.join(failed_monitoring)}"
            
            return {
                "name": "monitoring_check",
                "category": "observability",
                "status": ReadinessStatus.PASSED.value if passed else ReadinessStatus.FAILED.value,
                "message": message,
                "details": monitoring_status,
                "severity": "low" if not passed else "info",
                "waivable": True,
                "remediation_url": "https://docs.prodsprints.ai/readiness/monitoring",
                "estimated_fix_time_minutes": 60 if not passed else 0,
            }
            
        except Exception as e:
            return {
                "name": "monitoring_check",
                "category": "observability",
                "status": ReadinessStatus.FAILED.value,
                "message": f"Monitoring check failed: {str(e)}",
                "severity": "low",
                "waivable": True,
            }
    
    async def generate_readiness_report(self, project_id: str, readiness_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive readiness report."""
        try:
            checks = readiness_data.get("checks", [])
            
            # Categorize checks
            categories = {}
            for check in checks:
                category = check.get("category", "other")
                if category not in categories:
                    categories[category] = {"passed": 0, "failed": 0, "total": 0}
                
                categories[category]["total"] += 1
                if check["status"] == ReadinessStatus.PASSED.value:
                    categories[category]["passed"] += 1
                else:
                    categories[category]["failed"] += 1
            
            # Generate recommendations
            recommendations = []
            failed_checks = [c for c in checks if c["status"] == ReadinessStatus.FAILED.value]
            
            for check in failed_checks:
                if check.get("estimated_fix_time_minutes", 0) > 0:
                    recommendations.append({
                        "check": check["name"],
                        "priority": self._get_priority_from_severity(check.get("severity", "medium")),
                        "description": check["message"],
                        "estimated_time": check["estimated_fix_time_minutes"],
                        "remediation_url": check.get("remediation_url"),
                    })
            
            # Sort recommendations by priority and time
            recommendations.sort(key=lambda x: (
                {"high": 0, "medium": 1, "low": 2}[x["priority"]],
                x["estimated_time"]
            ))
            
            return {
                "project_id": project_id,
                "report_id": f"report-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "overall_status": readiness_data.get("overall_status", "unknown"),
                "overall_score": readiness_data.get("overall_score", 0),
                "categories": categories,
                "total_checks": len(checks),
                "passed_checks": len([c for c in checks if c["status"] == ReadinessStatus.PASSED.value]),
                "failed_checks": len(failed_checks),
                "blockers": readiness_data.get("blockers", []),
                "recommendations": recommendations[:10],  # Top 10 recommendations
                "estimated_fix_time_total": sum(r["estimated_time"] for r in recommendations),
                "next_steps": self._generate_next_steps(readiness_data),
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate readiness report: {str(e)}")
    
    def _get_priority_from_severity(self, severity: str) -> str:
        """Convert severity to priority."""
        severity_to_priority = {
            "critical": "high",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "low",
        }
        return severity_to_priority.get(severity, "medium")
    
    def _generate_next_steps(self, readiness_data: Dict[str, Any]) -> List[str]:
        """Generate next steps based on readiness status."""
        overall_status = readiness_data.get("overall_status", "unknown")
        blockers = readiness_data.get("blockers", [])
        
        if overall_status == "ready":
            return [
                "✅ All readiness checks passed - ready for deployment",
                "Consider running a final smoke test before production release",
                "Review deployment strategy (blue-green, canary, etc.)",
                "Ensure monitoring and alerting are configured",
            ]
        elif overall_status == "blocked":
            steps = ["🚫 Deployment is blocked - resolve critical issues first:"]
            steps.extend([f"  • {blocker}" for blocker in blockers[:5]])
            if len(blockers) > 5:
                steps.append(f"  • ... and {len(blockers) - 5} more issues")
            return steps
        else:
            return [
                "⚠️ Some readiness checks need attention",
                "Review failed checks and implement fixes",
                "Consider waiving non-critical issues if needed",
                "Re-run readiness checks after fixes",
                "Proceed with deployment once score > 80%",
            ]
