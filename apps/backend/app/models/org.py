"""
Organization, user, and workspace models.
"""

from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship

from .base import Base


class Org(Base):
    """Organization model."""
    
    __tablename__ = "orgs"
    
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="free", nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="org", cascade="all, delete-orphan")
    workspaces = relationship("Workspace", back_populates="org", cascade="all, delete-orphan")


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=False)
    email = Column(CITEXT, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="member", nullable=False)
    tz = Column(String(50), default="UTC")
    
    # OAuth fields
    github_id = Column(String(255), unique=True)
    google_id = Column(String(255), unique=True)
    
    # Relationships
    org = relationship("Org", back_populates="users")
    created_workspaces = relationship("Workspace", back_populates="created_by_user")


class Workspace(Base):
    """Workspace model for project organization."""
    
    __tablename__ = "workspaces"
    
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    org = relationship("Org", back_populates="workspaces")
    created_by_user = relationship("User", back_populates="created_workspaces")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
