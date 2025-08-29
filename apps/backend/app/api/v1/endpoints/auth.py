"""
Authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    provider: str  # github, google
    code: str  # OAuth authorization code
    redirect_uri: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    org: dict
    workspace: dict


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """OAuth login endpoint."""
    # TODO: Implement OAuth flow
    return {
        "access_token": "mock_token",
        "token_type": "bearer", 
        "expires_in": 1800,
        "user": {
            "id": "user-123",
            "email": "user@example.com",
            "name": "Test User"
        },
        "org": {
            "id": "org-123",
            "name": "Test Org"
        },
        "workspace": {
            "id": "workspace-123", 
            "name": "Default Workspace"
        }
    }


@router.post("/logout")
async def logout(token: str = Depends(security)):
    """Logout endpoint."""
    # TODO: Implement token invalidation
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(token: str = Depends(security)):
    """Get current user info."""
    # TODO: Implement user info from token
    return {
        "id": "user-123",
        "email": "user@example.com", 
        "name": "Test User",
        "org_id": "org-123",
        "workspace_id": "workspace-123"
    }
