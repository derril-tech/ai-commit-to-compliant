"""
Test agent for generating and running tests.
"""

from typing import Dict, Any
from .base import BaseAgent


class TestAgent(BaseAgent):
    """Agent for test generation and execution."""
    
    async def setup(self) -> None:
        """Setup the test agent."""
        self.logger.info("Test agent setup complete")
    
    async def cleanup(self) -> None:
        """Cleanup the test agent."""
        self.logger.info("Test agent cleanup complete")
    
    async def subscribe_to_events(self) -> None:
        """Subscribe to test-related events."""
        await self.event_bus.subscribe("tests.generate", self.handle_test_generation)
        await self.event_bus.subscribe("tests.run", self.handle_test_execution)
    
    async def handle_test_generation(self, data: Dict[str, Any]) -> None:
        """Handle test generation request."""
        try:
            project_id = data["project_id"]
            audit_result = data["audit_result"]
            
            self.logger.info("Generating tests", project_id=project_id)
            
            # Generate test templates
            test_templates = await self.generate_test_templates(audit_result)
            
            # Publish tests generated event
            await self.publish_event("tests.generated", {
                "project_id": project_id,
                "test_templates": test_templates,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def handle_test_execution(self, data: Dict[str, Any]) -> None:
        """Handle test execution request."""
        try:
            project_id = data["project_id"]
            
            self.logger.info("Running tests", project_id=project_id)
            
            # Execute tests and collect results
            test_results = await self.run_tests(project_id)
            
            # Publish test results
            await self.publish_event("tests.completed", {
                "project_id": project_id,
                "test_results": test_results,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def generate_test_templates(self, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test templates based on audit results."""
        languages = audit_result.get("languages", {})
        frameworks = audit_result.get("frameworks", [])
        
        templates = {}
        
        if "JavaScript" in languages or "TypeScript" in languages:
            templates["jest_config"] = await self.generate_jest_config()
            templates["unit_tests"] = await self.generate_js_unit_tests(frameworks)
            templates["integration_tests"] = await self.generate_js_integration_tests(frameworks)
        
        if "Python" in languages:
            templates["pytest_config"] = await self.generate_pytest_config()
            templates["unit_tests"] = await self.generate_python_unit_tests(frameworks)
            templates["integration_tests"] = await self.generate_python_integration_tests(frameworks)
        
        return templates
    
    async def generate_jest_config(self) -> str:
        """Generate Jest configuration."""
        return '''module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/*.(test|spec).+(ts|tsx|js)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{ts,tsx}',
    '!src/**/index.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  testTimeout: 10000
};'''
    
    async def generate_js_unit_tests(self, frameworks: list) -> str:
        """Generate JavaScript/TypeScript unit test examples."""
        if "Next.js" in frameworks:
            return '''import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from '../src/pages/index';

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeInTheDocument();
  });

  it('has correct meta title', () => {
    render(<Home />);
    expect(document.title).toBe('ProdSprints AI');
  });
});

// API Route Test
import handler from '../src/pages/api/health';
import { createMocks } from 'node-mocks-http';

describe('/api/health', () => {
  it('returns health status', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(JSON.parse(res._getData())).toEqual({
      status: 'healthy'
    });
  });
});'''
        
        elif "FastAPI" in frameworks:
            return '''import request from 'supertest';
import app from '../src/app';

describe('API Endpoints', () => {
  it('GET /health returns 200', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);
    
    expect(response.body).toHaveProperty('status', 'healthy');
  });

  it('handles 404 for unknown routes', async () => {
    await request(app)
      .get('/unknown-route')
      .expect(404);
  });
});'''
        
        return '''import { sum, multiply } from '../src/utils/math';

describe('Math Utils', () => {
  describe('sum', () => {
    it('adds two positive numbers', () => {
      expect(sum(2, 3)).toBe(5);
    });

    it('handles negative numbers', () => {
      expect(sum(-1, 1)).toBe(0);
    });

    it('handles zero', () => {
      expect(sum(0, 5)).toBe(5);
    });
  });

  describe('multiply', () => {
    it('multiplies two numbers', () => {
      expect(multiply(3, 4)).toBe(12);
    });

    it('handles zero multiplication', () => {
      expect(multiply(5, 0)).toBe(0);
    });
  });
});'''
    
    async def generate_js_integration_tests(self, frameworks: list) -> str:
        """Generate JavaScript/TypeScript integration test examples."""
        return '''import { test, expect } from '@playwright/test';

test.describe('Application Integration', () => {
  test('user can navigate through the app', async ({ page }) => {
    await page.goto('/');
    
    // Check homepage loads
    await expect(page.locator('h1')).toContainText('ProdSprints AI');
    
    // Navigate to dashboard
    await page.click('text=Dashboard');
    await expect(page).toHaveURL('/dashboard');
    
    // Check dashboard content
    await expect(page.locator('[data-testid="project-list"]')).toBeVisible();
  });

  test('API integration works', async ({ request }) => {
    const response = await request.get('/api/projects');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
  });

  test('database integration', async ({ page }) => {
    // Test database operations through UI
    await page.goto('/projects/new');
    
    await page.fill('[data-testid="repo-url"]', 'https://github.com/test/repo');
    await page.click('[data-testid="import-button"]');
    
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });
});'''
    
    async def generate_pytest_config(self) -> str:
        """Generate pytest configuration."""
        return '''[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=80"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]'''
    
    async def generate_python_unit_tests(self, frameworks: list) -> str:
        """Generate Python unit test examples."""
        if "FastAPI" in frameworks:
            return '''import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.main import app
from src.core.database import get_db

client = TestClient(app)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = Mock()
        yield db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

class TestHealthEndpoint:
    def test_health_check_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

class TestProjectsAPI:
    def test_list_projects_empty(self):
        response = client.get("/v1/projects")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_project_success(self):
        project_data = {
            "repo_url": "https://github.com/test/repo",
            "branch": "main",
            "target": "vercel"
        }
        response = client.post("/v1/projects/import", json=project_data)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_create_project_invalid_url(self):
        project_data = {
            "repo_url": "invalid-url",
            "branch": "main",
            "target": "vercel"
        }
        response = client.post("/v1/projects/import", json=project_data)
        assert response.status_code == 422

class TestBusinessLogic:
    def test_calculate_cost_estimate(self):
        from src.services.cost_calculator import calculate_monthly_cost
        
        resources = {
            "compute": {"type": "t3.micro", "count": 1},
            "database": {"type": "db.t3.micro", "storage": 20},
            "storage": {"size_gb": 10}
        }
        
        cost = calculate_monthly_cost(resources)
        assert cost > 0
        assert isinstance(cost, float)

    @patch('src.services.github.GitHubService.get_repo_info')
    def test_repo_analysis(self, mock_get_repo):
        from src.services.repo_analyzer import analyze_repository
        
        mock_get_repo.return_value = {
            "name": "test-repo",
            "language": "Python",
            "size": 1024
        }
        
        result = analyze_repository("https://github.com/test/repo")
        assert result["language"] == "Python"
        mock_get_repo.assert_called_once()'''
        
        elif "Django" in frameworks:
            return '''import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from myapp.models import Project

class TestProjectModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_project(self):
        project = Project.objects.create(
            name='Test Project',
            repo_url='https://github.com/test/repo',
            owner=self.user
        )
        assert project.name == 'Test Project'
        assert str(project) == 'Test Project'

class TestProjectViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_project_list_requires_auth(self):
        response = self.client.get(reverse('project-list'))
        assert response.status_code == 302  # Redirect to login

    def test_project_list_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('project-list'))
        assert response.status_code == 200'''
        
        return '''import pytest
from unittest.mock import Mock, patch

from src.utils.calculator import add, multiply, divide
from src.services.data_processor import DataProcessor

class TestCalculatorUtils:
    def test_add_positive_numbers(self):
        assert add(2, 3) == 5

    def test_add_negative_numbers(self):
        assert add(-1, -1) == -2

    def test_multiply_by_zero(self):
        assert multiply(5, 0) == 0

    def test_divide_by_zero_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

class TestDataProcessor:
    def setUp(self):
        self.processor = DataProcessor()

    def test_process_valid_data(self):
        data = [1, 2, 3, 4, 5]
        result = self.processor.process(data)
        assert result["sum"] == 15
        assert result["average"] == 3.0

    def test_process_empty_data(self):
        with pytest.raises(ValueError):
            self.processor.process([])

    @patch('src.services.external_api.requests.get')
    def test_fetch_external_data(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.processor.fetch_external_data()
        assert result["status"] == "success"'''
    
    async def generate_python_integration_tests(self, frameworks: list) -> str:
        """Generate Python integration test examples."""
        return '''import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.core.database import Base, get_db
from src.core.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.mark.integration
class TestFullWorkflow:
    @pytest.mark.asyncio
    async def test_project_import_to_deployment(self):
        """Test complete workflow from project import to deployment."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. Import project
            import_response = await client.post("/v1/projects/import", json={
                "repo_url": "https://github.com/test/repo",
                "branch": "main",
                "target": "vercel"
            })
            assert import_response.status_code == 200
            project_id = import_response.json()["project_id"]

            # 2. Wait for audit to complete (simulate)
            await asyncio.sleep(1)

            # 3. Generate blueprint
            blueprint_response = await client.post("/v1/blueprints/generate", json={
                "project_id": project_id
            })
            assert blueprint_response.status_code == 200

            # 4. Check readiness
            readiness_response = await client.get(f"/v1/runs/readiness/{project_id}")
            assert readiness_response.status_code == 200

            # 5. Deploy (if ready)
            readiness_data = readiness_response.json()
            if readiness_data["overall_status"] == "ready":
                deploy_response = await client.post("/v1/releases/create", json={
                    "project_id": project_id,
                    "strategy": "blue-green"
                })
                assert deploy_response.status_code == 200

@pytest.mark.integration
class TestDatabaseIntegration:
    def test_database_connection(self):
        """Test database connectivity and basic operations."""
        from src.models.project import Project
        from src.core.database import SessionLocal

        db = SessionLocal()
        try:
            # Create test project
            project = Project(
                repo_url="https://github.com/test/repo",
                branch="main",
                target="vercel"
            )
            db.add(project)
            db.commit()
            db.refresh(project)

            # Verify project was created
            assert project.id is not None
            assert project.repo_url == "https://github.com/test/repo"

            # Clean up
            db.delete(project)
            db.commit()
        finally:
            db.close()

@pytest.mark.integration
class TestExternalServices:
    @pytest.mark.asyncio
    async def test_github_api_integration(self):
        """Test GitHub API integration."""
        from src.services.github import GitHubService
        
        github_service = GitHubService()
        
        # Test public repo access
        repo_info = await github_service.get_repo_info("octocat/Hello-World")
        assert repo_info["name"] == "Hello-World"
        assert repo_info["owner"]["login"] == "octocat"

    @pytest.mark.asyncio
    async def test_terraform_integration(self):
        """Test Terraform execution."""
        from src.services.terraform import TerraformService
        
        terraform_service = TerraformService()
        
        # Test terraform version
        version = await terraform_service.get_version()
        assert version.startswith("Terraform v")'''
    
    async def run_tests(self, project_id: str) -> Dict[str, Any]:
        """Run tests and return results."""
        # TODO: Implement actual test execution
        # This would involve running the test suite and collecting results
        
        # Mock test results for now
        return {
            "status": "passed",
            "total_tests": 45,
            "passed": 43,
            "failed": 2,
            "skipped": 0,
            "coverage": {
                "line_coverage": 85.2,
                "branch_coverage": 78.5,
                "function_coverage": 92.1,
            },
            "duration_ms": 12500,
            "failed_tests": [
                {
                    "name": "test_invalid_input",
                    "file": "tests/test_validation.py",
                    "error": "AssertionError: Expected validation error"
                },
                {
                    "name": "test_edge_case",
                    "file": "tests/test_utils.py", 
                    "error": "IndexError: list index out of range"
                }
            ]
        }
