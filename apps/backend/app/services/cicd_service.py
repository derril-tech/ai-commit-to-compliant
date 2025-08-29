"""
CI/CD service for generating and managing pipeline templates.
"""

import json
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from app.core.config import settings


class CICDService:
    """Service for managing CI/CD pipeline templates and deployment."""
    
    async def generate_workflow_templates(self, project_id: str, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CI/CD workflow templates based on project audit."""
        try:
            languages = audit_result.get("languages", {})
            frameworks = audit_result.get("frameworks", [])
            has_docker = audit_result.get("docker", {}).get("dockerfile", False)
            databases = audit_result.get("databases", [])
            
            templates = {}
            
            # Generate main CI/CD workflow
            if "JavaScript" in languages or "TypeScript" in languages:
                templates["ci-cd.yml"] = await self._generate_nodejs_workflow(frameworks, has_docker, databases)
            elif "Python" in languages:
                templates["ci-cd.yml"] = await self._generate_python_workflow(frameworks, has_docker, databases)
            else:
                templates["ci-cd.yml"] = await self._generate_generic_workflow(has_docker)
            
            # Generate security workflow
            templates["security.yml"] = await self._generate_security_workflow()
            
            # Generate dependency update workflow
            templates["dependency-update.yml"] = await self._generate_dependency_update_workflow(languages)
            
            # Generate performance testing workflow
            if has_docker:
                templates["performance.yml"] = await self._generate_performance_workflow()
            
            return {
                "project_id": project_id,
                "templates": templates,
                "template_count": len(templates),
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "workflow_features": self._get_workflow_features(templates),
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate workflow templates: {str(e)}")
    
    async def create_github_pr(self, project_id: str, repo_url: str, templates: Dict[str, str], branch_name: str = "prodsprints/setup-cicd") -> Dict[str, Any]:
        """Create a GitHub PR with CI/CD templates."""
        try:
            # TODO: Implement actual GitHub API integration
            # For now, simulate PR creation
            
            pr_data = {
                "pr_number": 123,
                "pr_url": f"{repo_url}/pull/123",
                "branch_name": branch_name,
                "title": "feat: Add ProdSprints AI CI/CD workflows",
                "description": self._generate_pr_description(templates),
                "files_changed": len(templates),
                "status": "open",
                "created_at": datetime.utcnow().isoformat() + "Z",
            }
            
            # In real implementation, this would:
            # 1. Clone the repository
            # 2. Create a new branch
            # 3. Add workflow files to .github/workflows/
            # 4. Commit and push changes
            # 5. Create pull request via GitHub API
            
            return pr_data
            
        except Exception as e:
            raise Exception(f"Failed to create GitHub PR: {str(e)}")
    
    async def setup_branch_protection(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """Setup branch protection rules."""
        try:
            # TODO: Implement actual GitHub API integration
            # For now, simulate branch protection setup
            
            protection_rules = {
                "required_status_checks": {
                    "strict": True,
                    "contexts": [
                        "ci/test",
                        "ci/lint",
                        "ci/security-scan",
                        "ci/build",
                    ]
                },
                "enforce_admins": False,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True,
                },
                "restrictions": None,
                "allow_force_pushes": False,
                "allow_deletions": False,
            }
            
            return {
                "branch": branch,
                "protection_enabled": True,
                "rules": protection_rules,
                "configured_at": datetime.utcnow().isoformat() + "Z",
            }
            
        except Exception as e:
            raise Exception(f"Failed to setup branch protection: {str(e)}")
    
    async def validate_workflow_syntax(self, workflow_content: str) -> Dict[str, Any]:
        """Validate GitHub Actions workflow syntax."""
        try:
            import yaml
            
            # Parse YAML to check for syntax errors
            parsed_yaml = yaml.safe_load(workflow_content)
            
            # Basic validation checks
            validation_errors = []
            validation_warnings = []
            
            # Check required fields
            if "name" not in parsed_yaml:
                validation_errors.append("Workflow must have a 'name' field")
            
            if "on" not in parsed_yaml:
                validation_errors.append("Workflow must have an 'on' field")
            
            if "jobs" not in parsed_yaml:
                validation_errors.append("Workflow must have a 'jobs' field")
            
            # Check job structure
            if "jobs" in parsed_yaml:
                for job_name, job_config in parsed_yaml["jobs"].items():
                    if "runs-on" not in job_config:
                        validation_errors.append(f"Job '{job_name}' must have 'runs-on' field")
                    
                    if "steps" not in job_config:
                        validation_errors.append(f"Job '{job_name}' must have 'steps' field")
            
            # Check for common issues
            if "actions/checkout" not in workflow_content:
                validation_warnings.append("Workflow should include actions/checkout step")
            
            return {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "warnings": validation_warnings,
                "parsed_successfully": True,
            }
            
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "errors": [f"YAML syntax error: {str(e)}"],
                "warnings": [],
                "parsed_successfully": False,
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "parsed_successfully": False,
            }
    
    async def _generate_nodejs_workflow(self, frameworks: List[str], has_docker: bool, databases: List[str]) -> str:
        """Generate Node.js/TypeScript workflow."""
        is_nextjs = "Next.js" in frameworks
        
        workflow = f'''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '18'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{{{ github.repository }}}}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:'''
        
        if "postgresql" in databases:
            workflow += '''
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432'''
        
        if "redis" in databases:
            workflow += '''
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379'''
        
        workflow += '''
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linting
        run: npm run lint
      
      - name: Run type checking
        run: npm run type-check
        if: ${{ hashFiles('tsconfig.json') != '' }}
      
      - name: Run tests
        run: npm test -- --coverage
        env:'''
        
        if "postgresql" in databases:
            workflow += '''
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test'''
        if "redis" in databases:
            workflow += '''
          REDIS_URL: redis://localhost:6379'''
        
        workflow += '''
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          fail_ci_if_error: true
      
      - name: Build application
        run: npm run build'''
        
        if is_nextjs:
            workflow += '''
      
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.12.x
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}'''
        
        workflow += '''

  security:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Audit npm dependencies
        run: npm audit --audit-level high'''
        
        if has_docker:
            workflow += '''

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha
            type=raw,value=latest,enable={{{{is_default_branch}}}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: spdx-json
          output-file: sbom.spdx.json
      
      - name: Sign container image
        run: |
          cosign sign --yes ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1
      
      - name: Attest SBOM
        run: |
          cosign attest --yes --predicate sbom.spdx.json --type spdxjson ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1'''
        
        workflow += '''

  deploy-staging:
    runs-on: ubuntu-latest
    needs: ''' + ("build" if has_docker else "security") + '''
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add deployment logic here
      
      - name: Run smoke tests
        run: |
          echo "Running smoke tests"
          # Add smoke test logic here
      
      - name: Notify deployment
        run: |
          echo "Staging deployment completed successfully"
'''
        
        return workflow
    
    async def _generate_python_workflow(self, frameworks: List[str], has_docker: bool, databases: List[str]) -> str:
        """Generate Python workflow."""
        is_fastapi = "FastAPI" in frameworks
        is_django = "Django" in frameworks
        
        workflow = f'''name: Python CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{{{ github.repository }}}}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:'''
        
        if "postgresql" in databases:
            workflow += '''
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432'''
        
        if "redis" in databases:
            workflow += '''
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379'''
        
        workflow += '''
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run linting
        run: |
          ruff check .
          ruff format --check .
      
      - name: Run type checking
        run: mypy .
        if: ${{ hashFiles('mypy.ini') != '' || hashFiles('.mypy.ini') != '' || hashFiles('pyproject.toml') != '' }}
      
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml --cov-report=html
        env:'''
        
        if "postgresql" in databases:
            workflow += '''
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test'''
        if "redis" in databases:
            workflow += '''
          REDIS_URL: redis://localhost:6379'''
        
        workflow += '''
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true'''
        
        if is_django:
            workflow += '''
      
      - name: Run Django checks
        run: |
          python manage.py check
          python manage.py makemigrations --check --dry-run'''
        
        workflow += '''

  security:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install security tools
        run: |
          python -m pip install --upgrade pip
          pip install safety bandit
      
      - name: Run safety check
        run: safety check
      
      - name: Run bandit security linter
        run: bandit -r . -f json -o bandit-report.json
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif''''
        
        if has_docker:
            workflow += '''

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Sign container image
        run: |
          cosign sign --yes ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1'''
        
        workflow += '''

  deploy-staging:
    runs-on: ubuntu-latest
    needs: ''' + ("build" if has_docker else "security") + '''
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add deployment logic here
      
      - name: Run smoke tests
        run: |
          echo "Running smoke tests"
          # Add smoke test logic here
'''
        
        return workflow
    
    async def _generate_generic_workflow(self, has_docker: bool) -> str:
        """Generate generic workflow for other languages."""
        return '''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run tests
        run: |
          echo "Add your test commands here"
          # Example: make test
      
      - name: Run linting
        run: |
          echo "Add your linting commands here"
          # Example: make lint

  security:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  deploy-staging:
    runs-on: ubuntu-latest
    needs: security
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add deployment logic here
'''
    
    async def _generate_security_workflow(self) -> str:
        """Generate security scanning workflow."""
        return '''name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    permissions:
      security-events: write
      actions: read
      contents: read
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run CodeQL Analysis
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python
      
      - name: Autobuild
        uses: github/codeql-action/autobuild@v2
      
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
      
      - name: Run OWASP ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://your-staging-url.com'
        continue-on-error: true
'''
    
    async def _generate_dependency_update_workflow(self, languages: Dict[str, int]) -> str:
        """Generate dependency update workflow."""
        workflow = '''name: Dependency Updates

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  update-dependencies:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
'''
        
        if "JavaScript" in languages or "TypeScript" in languages:
            workflow += '''
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Update npm dependencies
        run: |
          npm update
          npm audit fix --audit-level moderate
      
      - name: Create Pull Request for npm updates
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: update npm dependencies'
          title: 'chore: update npm dependencies'
          branch: dependency-updates/npm
          delete-branch: true'''
        
        if "Python" in languages:
            workflow += '''
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Update Python dependencies
        run: |
          pip install --upgrade pip pip-tools
          pip-compile --upgrade requirements.in
          pip-compile --upgrade requirements-dev.in
      
      - name: Create Pull Request for Python updates
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: update Python dependencies'
          title: 'chore: update Python dependencies'
          branch: dependency-updates/python
          delete-branch: true'''
        
        return workflow
    
    async def _generate_performance_workflow(self) -> str:
        """Generate performance testing workflow."""
        return '''name: Performance Tests

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 4 * * *'  # Daily at 4 AM
  workflow_dispatch:

jobs:
  performance-test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Run performance tests
        run: |
          k6 run --out json=performance-results.json performance/load-test.js
        env:
          TARGET_URL: https://your-staging-url.com
      
      - name: Upload performance results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: performance-results.json
      
      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('performance-results.json', 'utf8'));
            // Add logic to parse and comment performance results
'''
    
    def _generate_pr_description(self, templates: Dict[str, str]) -> str:
        """Generate PR description for CI/CD setup."""
        description = """## 🚀 ProdSprints AI CI/CD Setup

This PR adds comprehensive CI/CD workflows to your repository, including:

### ✅ Features Added
"""
        
        if "ci-cd.yml" in templates:
            description += "- **Main CI/CD Pipeline**: Automated testing, building, and deployment\n"
        
        if "security.yml" in templates:
            description += "- **Security Scanning**: Daily vulnerability scans with Trivy and CodeQL\n"
        
        if "dependency-update.yml" in templates:
            description += "- **Dependency Updates**: Automated weekly dependency updates\n"
        
        if "performance.yml" in templates:
            description += "- **Performance Testing**: Load testing with k6\n"
        
        description += """
### 🔧 Workflow Details
- **Testing**: Unit tests, integration tests, and code coverage
- **Security**: Vulnerability scanning, dependency auditing, SAST/DAST
- **Quality**: Linting, type checking, and code formatting
- **Building**: Docker image building with SBOM and signing
- **Deployment**: Automated staging deployment with smoke tests

### 🛡️ Security Features
- Container image signing with Cosign
- SBOM (Software Bill of Materials) generation
- Vulnerability scanning with Trivy
- Static analysis with CodeQL
- Dependency security auditing

### 📋 Next Steps
1. Review and merge this PR
2. Configure any required secrets in repository settings
3. Set up branch protection rules (optional - can be done automatically)
4. Customize deployment targets and environments

### 🔗 Documentation
- [ProdSprints AI Documentation](https://docs.prodsprints.ai)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---
*This PR was automatically generated by ProdSprints AI*
"""
        
        return description
    
    def _get_workflow_features(self, templates: Dict[str, str]) -> List[str]:
        """Extract features from generated workflows."""
        features = []
        
        for template_name, content in templates.items():
            if "coverage" in content:
                features.append("code_coverage")
            if "trivy" in content.lower():
                features.append("vulnerability_scanning")
            if "cosign" in content:
                features.append("container_signing")
            if "sbom" in content.lower():
                features.append("sbom_generation")
            if "k6" in content:
                features.append("performance_testing")
            if "codeql" in content.lower():
                features.append("static_analysis")
        
        return list(set(features))
