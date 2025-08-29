"""
Kubernetes service for GitOps and advanced deployment strategies.
"""

import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from app.core.config import settings


class KubernetesDeploymentStrategy(Enum):
    """Kubernetes deployment strategies."""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"


class KubernetesService:
    """Service for Kubernetes deployments and GitOps."""
    
    async def generate_k8s_manifests(self, project_id: str, audit_result: Dict[str, Any], environment: str = "production") -> Dict[str, Any]:
        """Generate Kubernetes manifests for a project."""
        try:
            services = audit_result.get("services", [])
            languages = audit_result.get("languages", {})
            databases = audit_result.get("databases", [])
            
            manifests = {}
            
            # Generate namespace
            manifests["namespace.yaml"] = self._generate_namespace(project_id, environment)
            
            # Generate deployments for each service
            for service in services:
                service_name = service.get("name", "app")
                service_type = service.get("type", "web")
                
                # Deployment
                manifests[f"{service_name}-deployment.yaml"] = self._generate_deployment(
                    project_id, service_name, service_type, environment
                )
                
                # Service
                manifests[f"{service_name}-service.yaml"] = self._generate_service(
                    project_id, service_name, service_type
                )
                
                # Ingress (for web services)
                if service_type in ["web", "api", "frontend"]:
                    manifests[f"{service_name}-ingress.yaml"] = self._generate_ingress(
                        project_id, service_name, environment
                    )
                
                # HPA (Horizontal Pod Autoscaler)
                manifests[f"{service_name}-hpa.yaml"] = self._generate_hpa(
                    project_id, service_name
                )
            
            # Generate database manifests if needed
            for db in databases:
                if db == "postgresql":
                    manifests["postgres-deployment.yaml"] = self._generate_postgres_deployment(project_id, environment)
                    manifests["postgres-service.yaml"] = self._generate_postgres_service(project_id)
                    manifests["postgres-pvc.yaml"] = self._generate_postgres_pvc(project_id)
                elif db == "redis":
                    manifests["redis-deployment.yaml"] = self._generate_redis_deployment(project_id, environment)
                    manifests["redis-service.yaml"] = self._generate_redis_service(project_id)
            
            # Generate ConfigMaps and Secrets
            manifests["configmap.yaml"] = self._generate_configmap(project_id, environment)
            manifests["secrets.yaml"] = self._generate_secrets(project_id, environment)
            
            # Generate NetworkPolicies
            manifests["network-policy.yaml"] = self._generate_network_policy(project_id)
            
            # Generate ServiceMonitor for Prometheus
            manifests["service-monitor.yaml"] = self._generate_service_monitor(project_id)
            
            return {
                "project_id": project_id,
                "environment": environment,
                "manifests": manifests,
                "manifest_count": len(manifests),
                "generated_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate Kubernetes manifests: {str(e)}")
    
    async def generate_argocd_application(self, project_id: str, git_repo: str, environment: str = "production") -> Dict[str, Any]:
        """Generate ArgoCD Application manifest for GitOps."""
        try:
            app_manifest = {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "Application",
                "metadata": {
                    "name": f"{project_id}-{environment}",
                    "namespace": "argocd",
                    "labels": {
                        "app.kubernetes.io/name": project_id,
                        "app.kubernetes.io/instance": environment,
                        "prodsprints.ai/project": project_id,
                        "prodsprints.ai/environment": environment,
                    },
                    "finalizers": ["resources-finalizer.argocd.argoproj.io"],
                },
                "spec": {
                    "project": "default",
                    "source": {
                        "repoURL": git_repo,
                        "targetRevision": "HEAD",
                        "path": f"k8s/{environment}",
                    },
                    "destination": {
                        "server": "https://kubernetes.default.svc",
                        "namespace": f"{project_id}-{environment}",
                    },
                    "syncPolicy": {
                        "automated": {
                            "prune": True,
                            "selfHeal": True,
                        },
                        "syncOptions": [
                            "CreateNamespace=true",
                            "PrunePropagationPolicy=foreground",
                            "PruneLast=true",
                        ],
                    },
                    "revisionHistoryLimit": 10,
                },
            }
            
            return {
                "project_id": project_id,
                "environment": environment,
                "application_manifest": yaml.dump(app_manifest, default_flow_style=False),
                "argocd_url": f"{settings.ARGOCD_URL}/applications/{project_id}-{environment}",
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate ArgoCD application: {str(e)}")
    
    async def create_gitops_pr(self, project_id: str, git_repo: str, manifests: Dict[str, str], environment: str = "production") -> Dict[str, Any]:
        """Create GitOps PR with Kubernetes manifests."""
        try:
            # TODO: Implement actual Git operations
            # For now, simulate PR creation
            
            branch_name = f"prodsprints/k8s-{environment}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            pr_data = {
                "pr_number": 456,
                "pr_url": f"{git_repo}/pull/456",
                "branch_name": branch_name,
                "title": f"feat: Add Kubernetes manifests for {environment}",
                "description": self._generate_gitops_pr_description(project_id, environment, manifests),
                "files_changed": len(manifests),
                "status": "open",
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            
            return pr_data
            
        except Exception as e:
            raise Exception(f"Failed to create GitOps PR: {str(e)}")
    
    async def deploy_with_argo(self, project_id: str, environment: str, strategy: str = "rolling_update") -> Dict[str, Any]:
        """Deploy using ArgoCD with specified strategy."""
        try:
            deployment_id = f"k8s-deploy-{project_id}-{environment}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # TODO: Implement actual ArgoCD API calls
            # For now, simulate deployment
            
            return {
                "deployment_id": deployment_id,
                "project_id": project_id,
                "environment": environment,
                "strategy": strategy,
                "status": "syncing",
                "argocd_app_url": f"{settings.ARGOCD_URL}/applications/{project_id}-{environment}",
                "started_at": datetime.utcnow().isoformat() + "Z",
                "estimated_duration_minutes": 10,
            }
            
        except Exception as e:
            raise Exception(f"Failed to deploy with ArgoCD: {str(e)}")
    
    def _generate_namespace(self, project_id: str, environment: str) -> str:
        """Generate namespace manifest."""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": f"{project_id}-{environment}",
                "labels": {
                    "name": f"{project_id}-{environment}",
                    "prodsprints.ai/project": project_id,
                    "prodsprints.ai/environment": environment,
                },
            },
        }
        return yaml.dump(namespace, default_flow_style=False)
    
    def _generate_deployment(self, project_id: str, service_name: str, service_type: str, environment: str) -> str:
        """Generate deployment manifest."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{service_name}",
                "namespace": f"{project_id}-{environment}",
                "labels": {
                    "app": service_name,
                    "version": "v1",
                    "prodsprints.ai/project": project_id,
                    "prodsprints.ai/service": service_name,
                },
            },
            "spec": {
                "replicas": 3 if environment == "production" else 2,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1,
                    },
                },
                "selector": {
                    "matchLabels": {
                        "app": service_name,
                        "version": "v1",
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name,
                            "version": "v1",
                            "prodsprints.ai/project": project_id,
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8080",
                            "prometheus.io/path": "/metrics",
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": service_name,
                                "image": f"ghcr.io/{project_id}/{service_name}:latest",
                                "ports": [
                                    {
                                        "containerPort": 8080,
                                        "name": "http",
                                    },
                                ],
                                "env": [
                                    {
                                        "name": "ENVIRONMENT",
                                        "value": environment,
                                    },
                                    {
                                        "name": "SERVICE_NAME",
                                        "value": service_name,
                                    },
                                ],
                                "envFrom": [
                                    {
                                        "configMapRef": {
                                            "name": f"{project_id}-config",
                                        },
                                    },
                                    {
                                        "secretRef": {
                                            "name": f"{project_id}-secrets",
                                        },
                                    },
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi",
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "512Mi",
                                    },
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8080,
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8080,
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "runAsNonRoot": True,
                                    "runAsUser": 1000,
                                    "capabilities": {
                                        "drop": ["ALL"],
                                    },
                                },
                            },
                        ],
                        "securityContext": {
                            "fsGroup": 1000,
                        },
                        "serviceAccountName": f"{project_id}-sa",
                    },
                },
            },
        }
        return yaml.dump(deployment, default_flow_style=False)
    
    def _generate_service(self, project_id: str, service_name: str, service_type: str) -> str:
        """Generate service manifest."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{service_name}",
                "labels": {
                    "app": service_name,
                    "prodsprints.ai/project": project_id,
                },
            },
            "spec": {
                "selector": {
                    "app": service_name,
                },
                "ports": [
                    {
                        "port": 80,
                        "targetPort": 8080,
                        "name": "http",
                    },
                ],
                "type": "ClusterIP",
            },
        }
        return yaml.dump(service, default_flow_style=False)
    
    def _generate_ingress(self, project_id: str, service_name: str, environment: str) -> str:
        """Generate ingress manifest."""
        host = f"{project_id}-{environment}.prodsprints.ai" if environment != "production" else f"{project_id}.prodsprints.ai"
        
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{service_name}",
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                },
            },
            "spec": {
                "ingressClassName": "nginx",
                "tls": [
                    {
                        "hosts": [host],
                        "secretName": f"{service_name}-tls",
                    },
                ],
                "rules": [
                    {
                        "host": host,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": service_name,
                                            "port": {
                                                "number": 80,
                                            },
                                        },
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
        }
        return yaml.dump(ingress, default_flow_style=False)
    
    def _generate_hpa(self, project_id: str, service_name: str) -> str:
        """Generate HPA manifest."""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{service_name}",
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": service_name,
                },
                "minReplicas": 2,
                "maxReplicas": 10,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70,
                            },
                        },
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80,
                            },
                        },
                    },
                ],
            },
        }
        return yaml.dump(hpa, default_flow_style=False)
    
    def _generate_configmap(self, project_id: str, environment: str) -> str:
        """Generate ConfigMap manifest."""
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{project_id}-config",
            },
            "data": {
                "ENVIRONMENT": environment,
                "LOG_LEVEL": "info" if environment == "production" else "debug",
                "METRICS_ENABLED": "true",
                "TRACING_ENABLED": "true",
            },
        }
        return yaml.dump(configmap, default_flow_style=False)
    
    def _generate_secrets(self, project_id: str, environment: str) -> str:
        """Generate Secrets manifest."""
        secrets = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{project_id}-secrets",
            },
            "type": "Opaque",
            "stringData": {
                "DATABASE_URL": "postgresql://user:pass@postgres:5432/app",
                "REDIS_URL": "redis://redis:6379",
                "SECRET_KEY": "change-me-in-production",
            },
        }
        return yaml.dump(secrets, default_flow_style=False)
    
    def _generate_network_policy(self, project_id: str) -> str:
        """Generate NetworkPolicy manifest."""
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{project_id}-network-policy",
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "prodsprints.ai/project": project_id,
                    },
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "prodsprints.ai/project": project_id,
                                    },
                                },
                            },
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "name": "ingress-nginx",
                                    },
                                },
                            },
                        ],
                    },
                ],
                "egress": [
                    {
                        "to": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "prodsprints.ai/project": project_id,
                                    },
                                },
                            },
                        ],
                    },
                    {
                        "to": [],
                        "ports": [
                            {
                                "protocol": "TCP",
                                "port": 53,
                            },
                            {
                                "protocol": "UDP",
                                "port": 53,
                            },
                        ],
                    },
                ],
            },
        }
        return yaml.dump(network_policy, default_flow_style=False)
    
    def _generate_service_monitor(self, project_id: str) -> str:
        """Generate ServiceMonitor for Prometheus."""
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": f"{project_id}",
                "labels": {
                    "prodsprints.ai/project": project_id,
                },
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "prodsprints.ai/project": project_id,
                    },
                },
                "endpoints": [
                    {
                        "port": "http",
                        "path": "/metrics",
                        "interval": "30s",
                    },
                ],
            },
        }
        return yaml.dump(service_monitor, default_flow_style=False)
    
    def _generate_postgres_deployment(self, project_id: str, environment: str) -> str:
        """Generate PostgreSQL deployment."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "postgres",
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "postgres",
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "postgres",
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "postgres",
                                "image": "postgres:15",
                                "env": [
                                    {
                                        "name": "POSTGRES_DB",
                                        "value": "app",
                                    },
                                    {
                                        "name": "POSTGRES_USER",
                                        "value": "app_user",
                                    },
                                    {
                                        "name": "POSTGRES_PASSWORD",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": f"{project_id}-secrets",
                                                "key": "POSTGRES_PASSWORD",
                                            },
                                        },
                                    },
                                ],
                                "ports": [
                                    {
                                        "containerPort": 5432,
                                    },
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "postgres-storage",
                                        "mountPath": "/var/lib/postgresql/data",
                                    },
                                ],
                            },
                        ],
                        "volumes": [
                            {
                                "name": "postgres-storage",
                                "persistentVolumeClaim": {
                                    "claimName": "postgres-pvc",
                                },
                            },
                        ],
                    },
                },
            },
        }
        return yaml.dump(deployment, default_flow_style=False)
    
    def _generate_postgres_service(self, project_id: str) -> str:
        """Generate PostgreSQL service."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "postgres",
            },
            "spec": {
                "selector": {
                    "app": "postgres",
                },
                "ports": [
                    {
                        "port": 5432,
                        "targetPort": 5432,
                    },
                ],
            },
        }
        return yaml.dump(service, default_flow_style=False)
    
    def _generate_postgres_pvc(self, project_id: str) -> str:
        """Generate PostgreSQL PVC."""
        pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "postgres-pvc",
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {
                    "requests": {
                        "storage": "10Gi",
                    },
                },
            },
        }
        return yaml.dump(pvc, default_flow_style=False)
    
    def _generate_redis_deployment(self, project_id: str, environment: str) -> str:
        """Generate Redis deployment."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "redis",
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "redis",
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "redis",
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "redis",
                                "image": "redis:7",
                                "ports": [
                                    {
                                        "containerPort": 6379,
                                    },
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi",
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "256Mi",
                                    },
                                },
                            },
                        ],
                    },
                },
            },
        }
        return yaml.dump(deployment, default_flow_style=False)
    
    def _generate_redis_service(self, project_id: str) -> str:
        """Generate Redis service."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "redis",
            },
            "spec": {
                "selector": {
                    "app": "redis",
                },
                "ports": [
                    {
                        "port": 6379,
                        "targetPort": 6379,
                    },
                ],
            },
        }
        return yaml.dump(service, default_flow_style=False)
    
    def _generate_gitops_pr_description(self, project_id: str, environment: str, manifests: Dict[str, str]) -> str:
        """Generate GitOps PR description."""
        return f"""## 🚀 Kubernetes Deployment for {project_id} ({environment})

This PR adds Kubernetes manifests for deploying {project_id} to the {environment} environment.

### 📦 Manifests Added
- **Namespace**: Isolated environment for the application
- **Deployments**: Application workloads with health checks and resource limits
- **Services**: Internal service discovery and load balancing
- **Ingress**: External traffic routing with TLS termination
- **HPA**: Horizontal Pod Autoscaler for automatic scaling
- **ConfigMaps & Secrets**: Configuration and sensitive data management
- **NetworkPolicy**: Network security and traffic isolation
- **ServiceMonitor**: Prometheus metrics collection

### 🔧 Features
- **Security**: Non-root containers, security contexts, network policies
- **Observability**: Prometheus metrics, health checks, logging
- **Scalability**: Horizontal pod autoscaling based on CPU/memory
- **Reliability**: Rolling updates, readiness/liveness probes
- **GitOps**: Declarative configuration management

### 🎯 Deployment Strategy
- **Rolling Updates**: Zero-downtime deployments
- **Health Checks**: Automatic traffic routing based on readiness
- **Resource Limits**: Proper resource allocation and limits
- **Auto-scaling**: Scale based on demand (2-10 replicas)

### 📊 Monitoring
- Prometheus metrics collection enabled
- Health check endpoints configured
- Resource usage monitoring
- Application performance metrics

### 🔐 Security
- Network policies for traffic isolation
- Security contexts with non-root users
- Secrets management for sensitive data
- TLS termination at ingress

---
*This PR was automatically generated by ProdSprints AI*
"""
