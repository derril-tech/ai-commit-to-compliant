"""
CI/CD agent for generating pipeline templates.
"""

from typing import Dict, Any
from .base import BaseAgent


class CICDAgent(BaseAgent):
    """Agent for generating CI/CD pipeline templates."""
    
    async def setup(self) -> None:
        """Setup the CI/CD agent."""
        self.logger.info("CI/CD agent setup complete")
    
    async def cleanup(self) -> None:
        """Cleanup the CI/CD agent."""
        self.logger.info("CI/CD agent cleanup complete")
    
    async def subscribe_to_events(self) -> None:
        """Subscribe to CI/CD generation events."""
        await self.event_bus.subscribe("cicd.generate", self.handle_cicd_generation)
    
    async def handle_cicd_generation(self, data: Dict[str, Any]) -> None:
        """Handle CI/CD pipeline generation request."""
        try:
            project_id = data["project_id"]
            audit_result = data["audit_result"]
            
            self.logger.info("Generating CI/CD templates", project_id=project_id)
            
            # Generate CI/CD templates based on audit results
            cicd_templates = await self.generate_cicd_templates(audit_result)
            
            # Publish CI/CD templates ready event
            await self.publish_event("cicd.templates_ready", {
                "project_id": project_id,
                "cicd_templates": cicd_templates,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def generate_cicd_templates(self, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CI/CD pipeline templates."""
        languages = audit_result.get("languages", {})
        frameworks = audit_result.get("frameworks", [])
        
        templates = {}
        
        # Generate GitHub Actions workflow
        if "JavaScript" in languages or "TypeScript" in languages:
            templates["github_actions_node"] = await self.generate_node_workflow(frameworks)
        
        if "Python" in languages:
            templates["github_actions_python"] = await self.generate_python_workflow(frameworks)
        
        # Generate common templates
        templates["security_scan"] = await self.generate_security_workflow()
        templates["docker_build"] = await self.generate_docker_workflow()
        
        return templates
    
    async def generate_node_workflow(self, frameworks: list) -> str:
        """Generate Node.js GitHub Actions workflow."""
        is_nextjs = "Next.js" in frameworks
        
        workflow = '''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '18'

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
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
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
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
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          fail_ci_if_error: true
      
      - name: Build application
        run: npm run build
'''

        if is_nextjs:
            workflow += '''
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.12.x
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
'''

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
        run: npm audit --audit-level high

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Sign container image
        run: |
          cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1

  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add deployment logic here
      
      - name: Run smoke tests
        run: |
          echo "Running smoke tests"
          # Add smoke test logic here
      
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # Add production deployment logic here
        if: success()
'''
        
        return workflow
    
    async def generate_python_workflow(self, frameworks: list) -> str:
        """Generate Python GitHub Actions workflow."""
        is_fastapi = "FastAPI" in frameworks
        is_django = "Django" in frameworks
        
        workflow = '''name: Python CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
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
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
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
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
'''

        if is_django:
            workflow += '''
      - name: Run Django checks
        run: |
          python manage.py check
          python manage.py makemigrations --check --dry-run
'''

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
      
      - name: Install dependencies
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
          sarif_file: 'trivy-results.sarif'

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Sign container image
        run: |
          cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1

  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add deployment logic here
      
      - name: Run smoke tests
        run: |
          echo "Running smoke tests"
          # Add smoke test logic here
      
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # Add production deployment logic here
        if: success()
'''
        
        return workflow
    
    async def generate_security_workflow(self) -> str:
        """Generate security scanning workflow."""
        return '''name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'table'
      
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
          target: 'https://your-app-url.com'
'''
    
    async def generate_docker_workflow(self) -> str:
        """Generate Docker build workflow."""
        return '''name: Docker Build

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  docker:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: spdx-json
          output-file: sbom.spdx.json
      
      - name: Sign container image
        run: |
          cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1
      
      - name: Attest SBOM
        run: |
          cosign attest --yes --predicate sbom.spdx.json --type spdxjson ghcr.io/${{ github.repository }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1
'''
