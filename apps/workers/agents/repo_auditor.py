"""
Repository auditor agent for analyzing codebases.
"""

import os
import tempfile
from typing import Dict, Any, List
from pathlib import Path

import git
import structlog

from .base import BaseAgent

logger = structlog.get_logger()


class RepoAuditorAgent(BaseAgent):
    """Agent for auditing repositories and detecting services, frameworks, etc."""
    
    async def setup(self) -> None:
        """Setup the repo auditor agent."""
        self.logger.info("Repo auditor agent setup complete")
    
    async def cleanup(self) -> None:
        """Cleanup the repo auditor agent."""
        self.logger.info("Repo auditor agent cleanup complete")
    
    async def subscribe_to_events(self) -> None:
        """Subscribe to project import events."""
        await self.event_bus.subscribe("project.imported", self.handle_project_import)
    
    async def handle_project_import(self, data: Dict[str, Any]) -> None:
        """Handle project import event and start audit."""
        try:
            project_id = data["project_id"]
            repo_url = data["repo_url"]
            branch = data.get("branch", "main")
            
            self.logger.info("Starting repo audit", project_id=project_id, repo_url=repo_url)
            
            # Clone and analyze repository
            audit_result = await self.audit_repository(repo_url, branch)
            
            # Publish audit complete event
            await self.publish_event("audit.completed", {
                "project_id": project_id,
                "audit_result": audit_result,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def audit_repository(self, repo_url: str, branch: str) -> Dict[str, Any]:
        """Audit a repository and return analysis results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repo"
            
            # Clone repository
            repo = git.Repo.clone_from(repo_url, repo_path, branch=branch, depth=1)
            
            # Analyze repository structure
            analysis = {
                "services": await self.detect_services(repo_path),
                "frameworks": await self.detect_frameworks(repo_path),
                "languages": await self.detect_languages(repo_path),
                "databases": await self.detect_databases(repo_path),
                "docker": await self.detect_docker(repo_path),
                "tests": await self.detect_tests(repo_path),
                "ci_cd": await self.detect_ci_cd(repo_path),
                "env_vars": await self.detect_env_vars(repo_path),
                "migrations": await self.detect_migrations(repo_path),
                "ports": await self.detect_ports(repo_path),
                "dependencies": await self.analyze_dependencies(repo_path),
            }
            
            return analysis
    
    async def detect_services(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Detect services in the repository."""
        services = []
        
        # Look for common service indicators
        service_files = [
            "package.json",
            "requirements.txt", 
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
        ]
        
        for root, dirs, files in os.walk(repo_path):
            root_path = Path(root)
            
            for file in files:
                if file in service_files:
                    service_name = root_path.name if root_path != repo_path else "main"
                    services.append({
                        "name": service_name,
                        "path": str(root_path.relative_to(repo_path)),
                        "type": self.infer_service_type(file),
                        "config_file": file,
                    })
        
        return services
    
    async def detect_frameworks(self, repo_path: Path) -> List[str]:
        """Detect frameworks used in the repository."""
        frameworks = []
        
        # Check package.json for JS/TS frameworks
        package_json = repo_path / "package.json"
        if package_json.exists():
            import json
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    if "next" in deps:
                        frameworks.append("Next.js")
                    elif "react" in deps:
                        frameworks.append("React")
                    elif "vue" in deps:
                        frameworks.append("Vue.js")
                    elif "express" in deps:
                        frameworks.append("Express.js")
                    elif "fastify" in deps:
                        frameworks.append("Fastify")
            except:
                pass
        
        # Check requirements.txt for Python frameworks
        requirements = repo_path / "requirements.txt"
        if requirements.exists():
            try:
                with open(requirements) as f:
                    content = f.read().lower()
                    if "fastapi" in content:
                        frameworks.append("FastAPI")
                    elif "django" in content:
                        frameworks.append("Django")
                    elif "flask" in content:
                        frameworks.append("Flask")
            except:
                pass
        
        return frameworks
    
    async def detect_languages(self, repo_path: Path) -> Dict[str, int]:
        """Detect programming languages and their file counts."""
        languages = {}
        
        language_extensions = {
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".jsx": "JavaScript",
            ".py": "Python",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
            ".kt": "Kotlin",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cs": "C#",
            ".cpp": "C++",
            ".c": "C",
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv"]]
            
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    async def detect_databases(self, repo_path: Path) -> List[str]:
        """Detect database usage."""
        databases = []
        
        # Check for database-related files and dependencies
        db_indicators = {
            "postgresql": ["psycopg2", "pg", "postgres"],
            "mysql": ["mysql", "pymysql"],
            "mongodb": ["mongodb", "mongoose", "pymongo"],
            "redis": ["redis", "ioredis"],
            "sqlite": ["sqlite3", "sqlite"],
        }
        
        # Check package.json
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    for db, indicators in db_indicators.items():
                        if any(indicator in deps for indicator in indicators):
                            databases.append(db)
            except:
                pass
        
        # Check requirements.txt
        requirements = repo_path / "requirements.txt"
        if requirements.exists():
            try:
                with open(requirements) as f:
                    content = f.read().lower()
                    
                    for db, indicators in db_indicators.items():
                        if any(indicator in content for indicator in indicators):
                            databases.append(db)
            except:
                pass
        
        return list(set(databases))
    
    async def detect_docker(self, repo_path: Path) -> Dict[str, Any]:
        """Detect Docker configuration."""
        docker_info = {
            "dockerfile": (repo_path / "Dockerfile").exists(),
            "docker_compose": (repo_path / "docker-compose.yml").exists() or (repo_path / "docker-compose.yaml").exists(),
            "dockerignore": (repo_path / ".dockerignore").exists(),
        }
        
        return docker_info
    
    async def detect_tests(self, repo_path: Path) -> Dict[str, Any]:
        """Detect test configuration and files."""
        test_info = {
            "test_files": 0,
            "test_frameworks": [],
            "coverage_config": False,
        }
        
        # Count test files
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if any(pattern in file.lower() for pattern in ["test", "spec"]):
                    test_info["test_files"] += 1
        
        # Check for test frameworks
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    test_frameworks = ["jest", "mocha", "jasmine", "vitest", "cypress", "playwright"]
                    for framework in test_frameworks:
                        if framework in deps:
                            test_info["test_frameworks"].append(framework)
            except:
                pass
        
        # Check for coverage config
        coverage_files = [".coveragerc", "coverage.xml", "jest.config.js", "vitest.config.ts"]
        test_info["coverage_config"] = any((repo_path / f).exists() for f in coverage_files)
        
        return test_info
    
    async def detect_ci_cd(self, repo_path: Path) -> Dict[str, Any]:
        """Detect CI/CD configuration."""
        ci_cd_info = {
            "github_actions": (repo_path / ".github" / "workflows").exists(),
            "gitlab_ci": (repo_path / ".gitlab-ci.yml").exists(),
            "jenkins": (repo_path / "Jenkinsfile").exists(),
            "circleci": (repo_path / ".circleci" / "config.yml").exists(),
        }
        
        return ci_cd_info
    
    async def detect_env_vars(self, repo_path: Path) -> List[str]:
        """Detect environment variable usage."""
        env_vars = set()
        
        # Check .env.example files
        env_files = [".env.example", ".env.template", ".env.sample"]
        for env_file in env_files:
            env_path = repo_path / env_file
            if env_path.exists():
                try:
                    with open(env_path) as f:
                        for line in f:
                            if "=" in line and not line.strip().startswith("#"):
                                var_name = line.split("=")[0].strip()
                                env_vars.add(var_name)
                except:
                    pass
        
        return list(env_vars)
    
    async def detect_migrations(self, repo_path: Path) -> Dict[str, Any]:
        """Detect database migrations."""
        migration_info = {
            "has_migrations": False,
            "migration_tool": None,
            "migration_count": 0,
        }
        
        # Check for common migration directories
        migration_dirs = [
            "migrations",
            "db/migrate",
            "database/migrations",
            "alembic/versions",
        ]
        
        for migration_dir in migration_dirs:
            dir_path = repo_path / migration_dir
            if dir_path.exists() and dir_path.is_dir():
                migration_files = list(dir_path.glob("*"))
                if migration_files:
                    migration_info["has_migrations"] = True
                    migration_info["migration_count"] = len(migration_files)
                    
                    if "alembic" in migration_dir:
                        migration_info["migration_tool"] = "alembic"
                    else:
                        migration_info["migration_tool"] = "unknown"
                    break
        
        return migration_info
    
    async def detect_ports(self, repo_path: Path) -> List[int]:
        """Detect ports used by the application."""
        ports = set()
        
        # Common port patterns to search for
        port_patterns = [
            r"PORT\s*=\s*(\d+)",
            r"port\s*:\s*(\d+)",
            r"listen\s*\(\s*(\d+)",
            r"\.listen\s*\(\s*(\d+)",
        ]
        
        import re
        
        # Search in common config files
        config_files = ["package.json", ".env.example", "docker-compose.yml", "Dockerfile"]
        
        for config_file in config_files:
            file_path = repo_path / config_file
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        content = f.read()
                        
                        for pattern in port_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                try:
                                    port = int(match)
                                    if 1000 <= port <= 65535:  # Valid port range
                                        ports.add(port)
                                except ValueError:
                                    pass
                except:
                    pass
        
        return sorted(list(ports))
    
    async def analyze_dependencies(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies."""
        deps_info = {
            "package_managers": [],
            "dependency_count": 0,
            "outdated_deps": [],
        }
        
        # Check for different package managers
        if (repo_path / "package.json").exists():
            deps_info["package_managers"].append("npm/yarn")
            try:
                import json
                with open(repo_path / "package.json") as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    deps_info["dependency_count"] += len(deps)
            except:
                pass
        
        if (repo_path / "requirements.txt").exists():
            deps_info["package_managers"].append("pip")
            try:
                with open(repo_path / "requirements.txt") as f:
                    deps_info["dependency_count"] += len([line for line in f if line.strip() and not line.startswith("#")])
            except:
                pass
        
        if (repo_path / "Cargo.toml").exists():
            deps_info["package_managers"].append("cargo")
        
        if (repo_path / "go.mod").exists():
            deps_info["package_managers"].append("go modules")
        
        return deps_info
    
    def infer_service_type(self, config_file: str) -> str:
        """Infer service type from config file."""
        type_mapping = {
            "package.json": "nodejs",
            "requirements.txt": "python",
            "Cargo.toml": "rust",
            "go.mod": "go",
            "pom.xml": "java",
            "build.gradle": "java",
        }
        
        return type_mapping.get(config_file, "unknown")
