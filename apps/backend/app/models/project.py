"""
Project, run, and artifact models.
"""

import enum
from sqlalchemy import Column, String, ForeignKey, Text, Integer, Enum, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class RunKind(enum.Enum):
    """Types of runs."""
    IMPORT = "import"
    BLUEPRINT = "blueprint"
    APPLY = "apply"
    READINESS = "readiness"
    RELEASE = "release"
    ROLLBACK = "rollback"


class RunStatus(enum.Enum):
    """Run status."""
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class ArtifactType(enum.Enum):
    """Types of artifacts."""
    IAC = "iac"
    CICD = "cicd"
    TESTS = "tests"
    SBOM = "sbom"
    PERF = "perf"
    OBSERVABILITY = "observability"
    RELEASE = "release"
    RUNBOOK = "runbook"


class Project(Base):
    """Project model."""
    
    __tablename__ = "projects"
    
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    repo_url = Column(Text, nullable=False)
    branch = Column(String(255), default="main", nullable=False)
    target = Column(String(100))  # deployment target (vercel, render, k8s)
    region = Column(String(50))
    state = Column(Text)  # current state/status
    
    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    integrations = relationship("Integration", back_populates="project", cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="project", cascade="all, delete-orphan")
    blueprint = relationship("Blueprint", back_populates="project", uselist=False, cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="project", cascade="all, delete-orphan")
    releases = relationship("Release", back_populates="project", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="project", cascade="all, delete-orphan")


class Integration(Base):
    """Project integrations (GitHub, cloud providers, etc.)."""
    
    __tablename__ = "integrations"
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True)
    type = Column(String(50), primary_key=True)  # github, aws, gcp, etc.
    creds_ref = Column(Text)  # encrypted credentials reference
    scopes = Column(ARRAY(String))  # permissions/scopes
    
    # Relationships
    project = relationship("Project", back_populates="integrations")


class Run(Base):
    """Execution run model."""
    
    __tablename__ = "runs"
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    kind = Column(Enum(RunKind), nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING, nullable=False)
    stage = Column(String(100))  # current stage within the run
    attempt = Column(Integer, default=0, nullable=False)
    logs_ref = Column(Text)  # reference to logs in object storage
    metrics = Column(JSONB)  # performance metrics
    policy_result = Column(JSONB)  # policy gate results
    
    # Relationships
    project = relationship("Project", back_populates="runs")
    artifacts = relationship("Artifact", back_populates="run", cascade="all, delete-orphan")


class Blueprint(Base):
    """Generated blueprint/plan for a project."""
    
    __tablename__ = "blueprints"
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True)
    iac_ref = Column(Text)  # reference to IaC templates
    cicd_ref = Column(Text)  # reference to CI/CD templates
    policies = Column(JSONB)  # policy configuration
    cost_estimate = Column(JSONB)  # cost projections
    plan_diff = Column(JSONB)  # diff preview
    
    # Relationships
    project = relationship("Project", back_populates="blueprint")


class Artifact(Base):
    """Generated artifacts (templates, configs, etc.)."""
    
    __tablename__ = "artifacts"
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    type = Column(Enum(ArtifactType), nullable=False)
    path = Column(Text, nullable=False)  # path in object storage
    meta = Column(JSONB)  # metadata
    
    # Relationships
    project = relationship("Project", back_populates="artifacts")
    run = relationship("Run", back_populates="artifacts")


class Release(Base):
    """Release model."""
    
    __tablename__ = "releases"
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    sha = Column(String(40), nullable=False)  # git commit SHA
    env = Column(String(50), nullable=False)  # staging, production
    strategy = Column(String(50), nullable=False)  # blue-green, canary
    status = Column(String(50), nullable=False)  # pending, active, rolled-back
    risk_score = Column(Numeric(3, 2))  # 0.00 to 1.00
    
    # Relationships
    project = relationship("Project", back_populates="releases")


class Alert(Base):
    """Alert/notification model."""
    
    __tablename__ = "alerts"
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    type = Column(String(50), nullable=False)  # security, performance, cost
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    action = Column(String(100))  # recommended action
    meta = Column(JSONB)  # alert details
    
    # Relationships
    project = relationship("Project", back_populates="alerts")
