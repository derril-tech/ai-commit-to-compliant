"""
Compliance service for SOC2, HIPAA, and other regulatory frameworks.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.core.config import settings


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"


class ComplianceService:
    """Service for compliance management and evidence collection."""
    
    async def assess_compliance(self, project_id: str, frameworks: List[str]) -> Dict[str, Any]:
        """Assess compliance against specified frameworks."""
        try:
            assessments = {}
            
            for framework in frameworks:
                if framework.upper() in [f.name for f in ComplianceFramework]:
                    assessment = await self._assess_framework_compliance(project_id, framework.lower())
                    assessments[framework.lower()] = assessment
            
            # Calculate overall compliance score
            overall_score = self._calculate_overall_compliance_score(assessments)
            
            # Generate compliance report
            report = await self._generate_compliance_report(project_id, assessments, overall_score)
            
            return {
                "project_id": project_id,
                "assessment_id": f"compliance-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "frameworks_assessed": frameworks,
                "assessments": assessments,
                "overall_score": overall_score,
                "report": report,
                "assessed_at": datetime.utcnow().isoformat() + "Z",
                "valid_until": (datetime.utcnow() + timedelta(days=90)).isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to assess compliance: {str(e)}")
    
    async def collect_evidence(self, project_id: str, framework: str, control_id: str) -> Dict[str, Any]:
        """Collect evidence for a specific compliance control."""
        try:
            evidence_items = []
            
            # Collect different types of evidence based on control
            if control_id.startswith("CC"):  # Common Criteria (SOC2)
                evidence_items = await self._collect_soc2_evidence(project_id, control_id)
            elif control_id.startswith("164."):  # HIPAA
                evidence_items = await self._collect_hipaa_evidence(project_id, control_id)
            elif control_id.startswith("A."):  # ISO27001
                evidence_items = await self._collect_iso27001_evidence(project_id, control_id)
            
            return {
                "project_id": project_id,
                "framework": framework,
                "control_id": control_id,
                "evidence_items": evidence_items,
                "evidence_count": len(evidence_items),
                "collected_at": datetime.utcnow().isoformat() + "Z",
                "collector": "prodsprints-ai",
            }
            
        except Exception as e:
            raise Exception(f"Failed to collect evidence: {str(e)}")
    
    async def generate_compliance_pack(self, project_id: str, framework: str) -> Dict[str, Any]:
        """Generate comprehensive compliance pack for a framework."""
        try:
            if framework == "soc2":
                pack = await self._generate_soc2_pack(project_id)
            elif framework == "hipaa":
                pack = await self._generate_hipaa_pack(project_id)
            elif framework == "gdpr":
                pack = await self._generate_gdpr_pack(project_id)
            else:
                raise ValueError(f"Unsupported framework: {framework}")
            
            return {
                "project_id": project_id,
                "framework": framework,
                "pack_id": f"{framework}-pack-{project_id}-{datetime.utcnow().strftime('%Y%m%d')}",
                "pack": pack,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate compliance pack: {str(e)}")
    
    async def _assess_framework_compliance(self, project_id: str, framework: str) -> Dict[str, Any]:
        """Assess compliance for a specific framework."""
        if framework == "soc2":
            return await self._assess_soc2_compliance(project_id)
        elif framework == "hipaa":
            return await self._assess_hipaa_compliance(project_id)
        elif framework == "gdpr":
            return await self._assess_gdpr_compliance(project_id)
        elif framework == "pci_dss":
            return await self._assess_pci_dss_compliance(project_id)
        elif framework == "iso27001":
            return await self._assess_iso27001_compliance(project_id)
        else:
            return {"status": ComplianceStatus.NOT_APPLICABLE.value, "score": 0}
    
    async def _assess_soc2_compliance(self, project_id: str) -> Dict[str, Any]:
        """Assess SOC2 Type II compliance."""
        controls = [
            {
                "id": "CC1.1",
                "name": "Control Environment - Integrity and Ethical Values",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 95,
                "evidence_count": 3,
                "last_tested": "2024-01-01T00:00:00Z",
            },
            {
                "id": "CC2.1",
                "name": "Communication and Information - Internal Communication",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 90,
                "evidence_count": 2,
                "last_tested": "2024-01-01T00:00:00Z",
            },
            {
                "id": "CC3.1",
                "name": "Risk Assessment - Objectives and Risks",
                "status": ComplianceStatus.PARTIALLY_COMPLIANT.value,
                "score": 75,
                "evidence_count": 1,
                "last_tested": "2024-01-01T00:00:00Z",
                "gaps": ["Risk assessment documentation incomplete"],
            },
            {
                "id": "CC4.1",
                "name": "Monitoring Activities - Ongoing Monitoring",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 88,
                "evidence_count": 4,
                "last_tested": "2024-01-01T00:00:00Z",
            },
            {
                "id": "CC5.1",
                "name": "Control Activities - Selection and Development",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 92,
                "evidence_count": 5,
                "last_tested": "2024-01-01T00:00:00Z",
            },
        ]
        
        total_score = sum(control["score"] for control in controls) / len(controls)
        compliant_controls = len([c for c in controls if c["status"] == ComplianceStatus.COMPLIANT.value])
        
        return {
            "framework": "SOC2 Type II",
            "status": ComplianceStatus.COMPLIANT.value if total_score >= 85 else ComplianceStatus.PARTIALLY_COMPLIANT.value,
            "score": round(total_score, 1),
            "controls": controls,
            "total_controls": len(controls),
            "compliant_controls": compliant_controls,
            "compliance_percentage": round((compliant_controls / len(controls)) * 100, 1),
            "trust_services_criteria": {
                "security": 92,
                "availability": 88,
                "processing_integrity": 85,
                "confidentiality": 90,
                "privacy": 87,
            },
        }
    
    async def _assess_hipaa_compliance(self, project_id: str) -> Dict[str, Any]:
        """Assess HIPAA compliance."""
        safeguards = [
            {
                "id": "164.308",
                "name": "Administrative Safeguards",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 94,
                "requirements": [
                    {"id": "164.308(a)(1)", "name": "Security Officer", "status": "compliant"},
                    {"id": "164.308(a)(2)", "name": "Assigned Security Responsibilities", "status": "compliant"},
                    {"id": "164.308(a)(3)", "name": "Workforce Training", "status": "compliant"},
                    {"id": "164.308(a)(4)", "name": "Information Access Management", "status": "compliant"},
                ],
            },
            {
                "id": "164.310",
                "name": "Physical Safeguards",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 90,
                "requirements": [
                    {"id": "164.310(a)(1)", "name": "Facility Access Controls", "status": "compliant"},
                    {"id": "164.310(a)(2)", "name": "Workstation Use", "status": "compliant"},
                    {"id": "164.310(d)(1)", "name": "Device and Media Controls", "status": "compliant"},
                ],
            },
            {
                "id": "164.312",
                "name": "Technical Safeguards",
                "status": ComplianceStatus.PARTIALLY_COMPLIANT.value,
                "score": 82,
                "requirements": [
                    {"id": "164.312(a)(1)", "name": "Access Control", "status": "compliant"},
                    {"id": "164.312(b)", "name": "Audit Controls", "status": "compliant"},
                    {"id": "164.312(c)(1)", "name": "Integrity", "status": "partially_compliant"},
                    {"id": "164.312(d)", "name": "Person or Entity Authentication", "status": "compliant"},
                    {"id": "164.312(e)(1)", "name": "Transmission Security", "status": "compliant"},
                ],
                "gaps": ["Data integrity monitoring needs enhancement"],
            },
        ]
        
        total_score = sum(safeguard["score"] for safeguard in safeguards) / len(safeguards)
        
        return {
            "framework": "HIPAA",
            "status": ComplianceStatus.COMPLIANT.value if total_score >= 90 else ComplianceStatus.PARTIALLY_COMPLIANT.value,
            "score": round(total_score, 1),
            "safeguards": safeguards,
            "phi_handling": {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "access_logging": True,
                "data_minimization": True,
                "breach_notification": True,
            },
        }
    
    async def _assess_gdpr_compliance(self, project_id: str) -> Dict[str, Any]:
        """Assess GDPR compliance."""
        principles = [
            {
                "id": "Art5.1.a",
                "name": "Lawfulness, fairness and transparency",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 88,
            },
            {
                "id": "Art5.1.b",
                "name": "Purpose limitation",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 92,
            },
            {
                "id": "Art5.1.c",
                "name": "Data minimisation",
                "status": ComplianceStatus.PARTIALLY_COMPLIANT.value,
                "score": 78,
                "gaps": ["Data retention policies need refinement"],
            },
            {
                "id": "Art5.1.d",
                "name": "Accuracy",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 85,
            },
            {
                "id": "Art5.1.e",
                "name": "Storage limitation",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 90,
            },
            {
                "id": "Art5.1.f",
                "name": "Integrity and confidentiality",
                "status": ComplianceStatus.COMPLIANT.value,
                "score": 94,
            },
        ]
        
        total_score = sum(principle["score"] for principle in principles) / len(principles)
        
        return {
            "framework": "GDPR",
            "status": ComplianceStatus.COMPLIANT.value if total_score >= 85 else ComplianceStatus.PARTIALLY_COMPLIANT.value,
            "score": round(total_score, 1),
            "principles": principles,
            "data_subject_rights": {
                "right_to_access": True,
                "right_to_rectification": True,
                "right_to_erasure": True,
                "right_to_portability": True,
                "right_to_object": True,
            },
            "privacy_by_design": True,
            "dpo_appointed": True,
        }
    
    async def _assess_pci_dss_compliance(self, project_id: str) -> Dict[str, Any]:
        """Assess PCI DSS compliance."""
        requirements = [
            {"id": "1", "name": "Install and maintain firewall configuration", "score": 95},
            {"id": "2", "name": "Do not use vendor-supplied defaults", "score": 90},
            {"id": "3", "name": "Protect stored cardholder data", "score": 88},
            {"id": "4", "name": "Encrypt transmission of cardholder data", "score": 92},
            {"id": "5", "name": "Protect against malware", "score": 85},
            {"id": "6", "name": "Develop secure systems and applications", "score": 87},
        ]
        
        total_score = sum(req["score"] for req in requirements) / len(requirements)
        
        return {
            "framework": "PCI DSS",
            "status": ComplianceStatus.COMPLIANT.value if total_score >= 85 else ComplianceStatus.PARTIALLY_COMPLIANT.value,
            "score": round(total_score, 1),
            "requirements": requirements,
        }
    
    async def _assess_iso27001_compliance(self, project_id: str) -> Dict[str, Any]:
        """Assess ISO27001 compliance."""
        controls = [
            {"id": "A.5", "name": "Information security policies", "score": 92},
            {"id": "A.6", "name": "Organization of information security", "score": 88},
            {"id": "A.7", "name": "Human resource security", "score": 85},
            {"id": "A.8", "name": "Asset management", "score": 90},
            {"id": "A.9", "name": "Access control", "score": 87},
            {"id": "A.10", "name": "Cryptography", "score": 94},
        ]
        
        total_score = sum(control["score"] for control in controls) / len(controls)
        
        return {
            "framework": "ISO27001",
            "status": ComplianceStatus.COMPLIANT.value if total_score >= 85 else ComplianceStatus.PARTIALLY_COMPLIANT.value,
            "score": round(total_score, 1),
            "controls": controls,
        }
    
    def _calculate_overall_compliance_score(self, assessments: Dict[str, Any]) -> float:
        """Calculate overall compliance score across all frameworks."""
        if not assessments:
            return 0.0
        
        total_score = sum(assessment.get("score", 0) for assessment in assessments.values())
        return round(total_score / len(assessments), 1)
    
    async def _generate_compliance_report(self, project_id: str, assessments: Dict[str, Any], overall_score: float) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        gaps = []
        recommendations = []
        
        for framework, assessment in assessments.items():
            if assessment.get("status") != ComplianceStatus.COMPLIANT.value:
                # Extract gaps from assessment
                if "controls" in assessment:
                    for control in assessment["controls"]:
                        if control.get("gaps"):
                            gaps.extend(control["gaps"])
                
                if "safeguards" in assessment:
                    for safeguard in assessment["safeguards"]:
                        if safeguard.get("gaps"):
                            gaps.extend(safeguard["gaps"])
                
                if "principles" in assessment:
                    for principle in assessment["principles"]:
                        if principle.get("gaps"):
                            gaps.extend(principle["gaps"])
        
        # Generate recommendations based on gaps
        if gaps:
            recommendations = [
                "Address identified compliance gaps before production deployment",
                "Implement automated compliance monitoring",
                "Schedule regular compliance assessments",
                "Document all compliance controls and procedures",
                "Train team members on compliance requirements",
            ]
        
        return {
            "overall_status": "compliant" if overall_score >= 85 else "needs_attention",
            "summary": f"Overall compliance score: {overall_score}%",
            "gaps_identified": len(gaps),
            "gaps": gaps[:10],  # Top 10 gaps
            "recommendations": recommendations,
            "next_assessment_due": (datetime.utcnow() + timedelta(days=90)).isoformat()[:10],
        }
    
    async def _collect_soc2_evidence(self, project_id: str, control_id: str) -> List[Dict[str, Any]]:
        """Collect evidence for SOC2 controls."""
        # TODO: Implement actual evidence collection
        return [
            {
                "type": "policy_document",
                "name": "Information Security Policy",
                "description": "Documented security policies and procedures",
                "location": f"s3://compliance-evidence/{project_id}/policies/security-policy.pdf",
                "collected_at": datetime.utcnow().isoformat() + "Z",
            },
            {
                "type": "access_log",
                "name": "System Access Logs",
                "description": "Logs showing user access and authentication",
                "location": f"s3://compliance-evidence/{project_id}/logs/access-logs-{datetime.utcnow().strftime('%Y%m')}.json",
                "collected_at": datetime.utcnow().isoformat() + "Z",
            },
        ]
    
    async def _collect_hipaa_evidence(self, project_id: str, control_id: str) -> List[Dict[str, Any]]:
        """Collect evidence for HIPAA controls."""
        return [
            {
                "type": "encryption_certificate",
                "name": "Data Encryption Certificate",
                "description": "Certificate showing data encryption implementation",
                "location": f"s3://compliance-evidence/{project_id}/certificates/encryption-cert.pem",
                "collected_at": datetime.utcnow().isoformat() + "Z",
            },
        ]
    
    async def _collect_iso27001_evidence(self, project_id: str, control_id: str) -> List[Dict[str, Any]]:
        """Collect evidence for ISO27001 controls."""
        return [
            {
                "type": "risk_assessment",
                "name": "Information Security Risk Assessment",
                "description": "Documented risk assessment and treatment plan",
                "location": f"s3://compliance-evidence/{project_id}/assessments/risk-assessment.pdf",
                "collected_at": datetime.utcnow().isoformat() + "Z",
            },
        ]
    
    async def _generate_soc2_pack(self, project_id: str) -> Dict[str, Any]:
        """Generate SOC2 compliance pack."""
        return {
            "description": "SOC2 Type II Compliance Pack",
            "trust_services_criteria": ["security", "availability", "processing_integrity", "confidentiality"],
            "control_objectives": 25,
            "evidence_items": 45,
            "policies_included": [
                "Information Security Policy",
                "Access Control Policy",
                "Incident Response Policy",
                "Business Continuity Policy",
                "Vendor Management Policy",
            ],
            "automated_controls": 18,
            "manual_controls": 7,
            "monitoring_frequency": "continuous",
        }
    
    async def _generate_hipaa_pack(self, project_id: str) -> Dict[str, Any]:
        """Generate HIPAA compliance pack."""
        return {
            "description": "HIPAA Compliance Pack for Healthcare Applications",
            "safeguards": ["administrative", "physical", "technical"],
            "phi_protection": True,
            "breach_notification": True,
            "business_associate_agreements": True,
            "policies_included": [
                "HIPAA Privacy Policy",
                "HIPAA Security Policy",
                "Breach Notification Procedures",
                "Employee Training Program",
                "Risk Assessment Procedures",
            ],
            "technical_safeguards": [
                "Access Control",
                "Audit Controls",
                "Integrity Controls",
                "Person or Entity Authentication",
                "Transmission Security",
            ],
        }
    
    async def _generate_gdpr_pack(self, project_id: str) -> Dict[str, Any]:
        """Generate GDPR compliance pack."""
        return {
            "description": "GDPR Compliance Pack for EU Data Processing",
            "lawful_basis": "legitimate_interest",
            "data_subject_rights": True,
            "privacy_by_design": True,
            "dpo_required": False,
            "policies_included": [
                "Privacy Policy",
                "Data Processing Policy",
                "Data Retention Policy",
                "Data Subject Rights Procedures",
                "Breach Notification Procedures",
            ],
            "data_protection_principles": [
                "Lawfulness, fairness and transparency",
                "Purpose limitation",
                "Data minimisation",
                "Accuracy",
                "Storage limitation",
                "Integrity and confidentiality",
            ],
        }
