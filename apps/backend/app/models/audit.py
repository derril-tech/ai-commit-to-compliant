"""
Audit log model for compliance and tracking.
"""

from sqlalchemy import Column, String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base


class AuditLog(Base):
    """Audit log for all user actions."""
    
    __tablename__ = "audit_log"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)  # Override UUID for performance
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # create, update, delete, approve, etc.
    target = Column(String(255), nullable=False)  # resource being acted upon
    meta = Column(JSONB)  # additional context
