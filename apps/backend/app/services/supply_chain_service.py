"""
Supply chain security service with Sigstore and SLSA provenance.
"""

import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from app.core.config import settings


class SLSALevel(Enum):
    """SLSA levels."""
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


class SupplyChainService:
    """Service for supply chain security and provenance."""
    
    async def generate_slsa_provenance(self, project_id: str, build_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SLSA provenance attestation."""
        try:
            # Build SLSA provenance statement
            provenance = {
                "_type": "https://in-toto.io/Statement/v0.1",
                "predicateType": "https://slsa.dev/provenance/v0.2",
                "subject": [
                    {
                        "name": build_context.get("artifact_name", f"{project_id}:latest"),
                        "digest": {
                            "sha256": build_context.get("artifact_digest", "abc123def456..."),
                        },
                    }
                ],
                "predicate": {
                    "builder": {
                        "id": "https://github.com/prodsprints-ai/builder@v1",
                    },
                    "buildType": "https://github.com/prodsprints-ai/build-type@v1",
                    "invocation": {
                        "configSource": {
                            "uri": build_context.get("repo_url", f"https://github.com/user/{project_id}"),
                            "digest": {
                                "sha1": build_context.get("commit_sha", "abc123def456"),
                            },
                            "entryPoint": build_context.get("workflow_path", ".github/workflows/ci.yml"),
                        },
                        "parameters": build_context.get("build_parameters", {}),
                        "environment": {
                            "github": {
                                "actor": build_context.get("actor", "prodsprints-ai"),
                                "event_name": build_context.get("event_name", "push"),
                                "ref": build_context.get("ref", "refs/heads/main"),
                                "repository": build_context.get("repository", f"user/{project_id}"),
                                "run_id": build_context.get("run_id", "123456789"),
                                "sha": build_context.get("commit_sha", "abc123def456"),
                            },
                        },
                    },
                    "metadata": {
                        "buildInvocationId": build_context.get("build_id", f"build-{project_id}-001"),
                        "buildStartedOn": build_context.get("build_started", datetime.utcnow().isoformat() + "Z"),
                        "buildFinishedOn": build_context.get("build_finished", datetime.utcnow().isoformat() + "Z"),
                        "completeness": {
                            "parameters": True,
                            "environment": True,
                            "materials": True,
                        },
                        "reproducible": False,
                    },
                    "materials": [
                        {
                            "uri": build_context.get("repo_url", f"https://github.com/user/{project_id}"),
                            "digest": {
                                "sha1": build_context.get("commit_sha", "abc123def456"),
                            },
                        }
                    ],
                },
            }
            
            # Sign the provenance with Sigstore
            signed_provenance = await self._sign_with_sigstore(provenance)
            
            # Calculate SLSA level
            slsa_level = await self._calculate_slsa_level(build_context)
            
            return {
                "project_id": project_id,
                "provenance_id": f"slsa-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "slsa_level": slsa_level.value,
                "provenance": provenance,
                "signed_provenance": signed_provenance,
                "attestation_url": f"https://rekor.sigstore.dev/api/v1/log/entries/{signed_provenance.get('log_index', 'unknown')}",
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate SLSA provenance: {str(e)}")
    
    async def sign_artifact(self, project_id: str, artifact_digest: str, artifact_type: str = "container") -> Dict[str, Any]:
        """Sign artifact with Sigstore Cosign."""
        try:
            # TODO: Implement actual Cosign signing
            # For now, simulate signing process
            
            signature_data = {
                "artifact_digest": artifact_digest,
                "artifact_type": artifact_type,
                "signature": "MEUCIQDxyz123...",  # Mock signature
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
                "bundle": {
                    "mediaType": "application/vnd.dev.sigstore.bundle+json;version=0.1",
                    "verificationMaterial": {
                        "tlogEntries": [
                            {
                                "logIndex": "12345678",
                                "logId": {
                                    "keyId": "wNI9atQGlz+VWfO6LRygH4QUfY/8W4RFwiT5i5WRgB0="
                                },
                                "kindVersion": {
                                    "kind": "hashedrekord",
                                    "version": "0.0.1"
                                },
                                "integratedTime": int(datetime.utcnow().timestamp()),
                            }
                        ],
                        "certificateChain": {
                            "certificates": [
                                {
                                    "rawBytes": "LS0tLS1CRUdJTi..."  # Base64 encoded cert
                                }
                            ]
                        }
                    },
                    "dsseEnvelope": {
                        "payload": base64.b64encode(json.dumps({
                            "_type": "https://in-toto.io/Statement/v0.1",
                            "predicateType": "https://cosign.sigstore.dev/attestation/v1",
                            "subject": [{"name": f"{project_id}@{artifact_digest}"}]
                        }).encode()).decode(),
                        "payloadType": "application/vnd.in-toto+json",
                        "signatures": [
                            {
                                "sig": "MEUCIQDxyz123..."
                            }
                        ]
                    }
                }
            }
            
            return {
                "project_id": project_id,
                "artifact_digest": artifact_digest,
                "signature_id": f"sig-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "signature_data": signature_data,
                "transparency_log_entry": f"https://rekor.sigstore.dev/api/v1/log/entries/12345678",
                "signed_at": datetime.utcnow().isoformat() + "Z",
                "valid": True,
            }
            
        except Exception as e:
            raise Exception(f"Failed to sign artifact: {str(e)}")
    
    async def verify_artifact_signature(self, project_id: str, artifact_digest: str, signature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify artifact signature using Sigstore."""
        try:
            # TODO: Implement actual signature verification
            # For now, simulate verification
            
            verification_result = {
                "verified": True,
                "certificate_valid": True,
                "certificate_identity": "prodsprints-ai@github.com",
                "certificate_issuer": "https://token.actions.githubusercontent.com",
                "transparency_log_verified": True,
                "policy_violations": [],
                "verification_time": datetime.utcnow().isoformat() + "Z",
            }
            
            return {
                "project_id": project_id,
                "artifact_digest": artifact_digest,
                "verification_result": verification_result,
                "verified_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to verify artifact signature: {str(e)}")
    
    async def generate_sbom(self, project_id: str, build_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Software Bill of Materials (SBOM)."""
        try:
            # TODO: Implement actual SBOM generation using tools like Syft
            # For now, generate mock SBOM
            
            sbom = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.4",
                "serialNumber": f"urn:uuid:sbom-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "version": 1,
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "tools": [
                        {
                            "vendor": "ProdSprints AI",
                            "name": "sbom-generator",
                            "version": "1.0.0",
                        }
                    ],
                    "component": {
                        "type": "application",
                        "bom-ref": f"{project_id}@latest",
                        "name": project_id,
                        "version": build_context.get("version", "latest"),
                    },
                },
                "components": [
                    {
                        "type": "library",
                        "bom-ref": "pkg:npm/express@4.18.2",
                        "name": "express",
                        "version": "4.18.2",
                        "purl": "pkg:npm/express@4.18.2",
                        "licenses": [{"license": {"id": "MIT"}}],
                        "hashes": [
                            {
                                "alg": "SHA-256",
                                "content": "abc123def456..."
                            }
                        ],
                    },
                    {
                        "type": "library",
                        "bom-ref": "pkg:npm/react@18.2.0",
                        "name": "react",
                        "version": "18.2.0",
                        "purl": "pkg:npm/react@18.2.0",
                        "licenses": [{"license": {"id": "MIT"}}],
                        "hashes": [
                            {
                                "alg": "SHA-256",
                                "content": "def456ghi789..."
                            }
                        ],
                    },
                ],
                "dependencies": [
                    {
                        "ref": f"{project_id}@latest",
                        "dependsOn": [
                            "pkg:npm/express@4.18.2",
                            "pkg:npm/react@18.2.0",
                        ],
                    }
                ],
            }
            
            # Sign SBOM
            signed_sbom = await self._sign_with_sigstore(sbom)
            
            return {
                "project_id": project_id,
                "sbom_id": f"sbom-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "sbom": sbom,
                "signed_sbom": signed_sbom,
                "component_count": len(sbom["components"]),
                "license_summary": self._analyze_licenses(sbom["components"]),
                "vulnerability_summary": await self._analyze_vulnerabilities(sbom["components"]),
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate SBOM: {str(e)}")
    
    async def assess_supply_chain_risk(self, project_id: str, sbom: Dict[str, Any]) -> Dict[str, Any]:
        """Assess supply chain security risks."""
        try:
            risk_factors = []
            
            components = sbom.get("components", [])
            
            # Analyze component risks
            for component in components:
                component_risk = await self._assess_component_risk(component)
                if component_risk:
                    risk_factors.append(component_risk)
            
            # Calculate overall risk score
            if risk_factors:
                total_score = sum(factor["score"] for factor in risk_factors)
                avg_score = total_score / len(risk_factors)
            else:
                avg_score = 1.0  # Low risk if no components
            
            # Determine risk level
            if avg_score >= 8:
                risk_level = "critical"
            elif avg_score >= 6:
                risk_level = "high"
            elif avg_score >= 4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "project_id": project_id,
                "risk_assessment_id": f"supply-chain-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "overall_risk_score": round(avg_score, 2),
                "risk_level": risk_level,
                "total_components": len(components),
                "risky_components": len(risk_factors),
                "risk_factors": risk_factors,
                "recommendations": self._generate_supply_chain_recommendations(risk_factors),
                "assessed_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to assess supply chain risk: {str(e)}")
    
    async def _sign_with_sigstore(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sign payload with Sigstore."""
        # TODO: Implement actual Sigstore signing
        # For now, return mock signed data
        return {
            "signature": "MEUCIQDxyz123...",
            "certificate": "-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----",
            "log_index": "12345678",
            "log_entry_url": "https://rekor.sigstore.dev/api/v1/log/entries/12345678",
            "signed_at": datetime.utcnow().isoformat() + "Z",
        }
    
    async def _calculate_slsa_level(self, build_context: Dict[str, Any]) -> SLSALevel:
        """Calculate SLSA level based on build context."""
        # Simplified SLSA level calculation
        score = 0
        
        # Source requirements
        if build_context.get("source_controlled", True):
            score += 1
        
        # Build requirements
        if build_context.get("build_service", True):
            score += 1
        
        # Provenance requirements
        if build_context.get("provenance_generated", True):
            score += 1
        
        # Isolation requirements
        if build_context.get("isolated_build", False):
            score += 1
        
        return SLSALevel(min(score, 3))
    
    def _analyze_licenses(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze component licenses."""
        license_counts = {}
        risky_licenses = []
        
        for component in components:
            licenses = component.get("licenses", [])
            for license_info in licenses:
                license_id = license_info.get("license", {}).get("id", "Unknown")
                license_counts[license_id] = license_counts.get(license_id, 0) + 1
                
                # Check for risky licenses
                if license_id in ["GPL-3.0", "AGPL-3.0", "SSPL-1.0"]:
                    risky_licenses.append({
                        "component": component.get("name"),
                        "license": license_id,
                        "risk": "copyleft",
                    })
        
        return {
            "total_licenses": len(license_counts),
            "license_distribution": license_counts,
            "risky_licenses": risky_licenses,
            "compliance_issues": len(risky_licenses),
        }
    
    async def _analyze_vulnerabilities(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze component vulnerabilities."""
        # TODO: Integrate with actual vulnerability databases
        # For now, return mock vulnerability data
        
        return {
            "total_vulnerabilities": 5,
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 2,
            "vulnerable_components": 3,
            "patched_available": 2,
        }
    
    async def _assess_component_risk(self, component: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Assess risk for individual component."""
        component_name = component.get("name", "unknown")
        component_version = component.get("version", "unknown")
        
        # Mock risk assessment
        # In real implementation, this would check:
        # - Known vulnerabilities
        # - Maintenance status
        # - License compatibility
        # - Supply chain attacks
        
        # Simulate some components being risky
        if component_name in ["express", "lodash", "moment"]:
            return {
                "component": component_name,
                "version": component_version,
                "score": 6.5,
                "risk_factors": [
                    "Known security vulnerabilities",
                    "Outdated version",
                ],
                "recommendation": f"Update {component_name} to latest version",
            }
        
        return None
    
    def _generate_supply_chain_recommendations(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate supply chain security recommendations."""
        recommendations = []
        
        if risk_factors:
            recommendations.extend([
                "Update vulnerable dependencies to latest versions",
                "Implement automated dependency scanning in CI/CD",
                "Use dependency pinning to ensure reproducible builds",
                "Monitor for new vulnerabilities in dependencies",
                "Consider using alternative packages with better security records",
            ])
        
        recommendations.extend([
            "Sign all container images with Cosign",
            "Generate and verify SLSA provenance for all builds",
            "Implement SBOM generation for all releases",
            "Use private package registries for internal dependencies",
            "Regularly audit and review third-party dependencies",
        ])
        
        return recommendations[:10]  # Top 10 recommendations
