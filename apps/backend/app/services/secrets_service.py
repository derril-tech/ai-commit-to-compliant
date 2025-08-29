"""
Secrets management service for secure credential handling.
"""

import base64
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class SecretsService:
    """Service for managing secrets and credentials."""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    async def store_secret(self, project_id: str, key: str, value: str, environment: str = "staging") -> Dict[str, Any]:
        """Store an encrypted secret."""
        try:
            # Encrypt the secret value
            encrypted_value = self.cipher.encrypt(value.encode())
            
            # Create secret metadata
            secret_data = {
                "project_id": project_id,
                "key": key,
                "encrypted_value": base64.b64encode(encrypted_value).decode(),
                "environment": environment,
                "created_at": datetime.utcnow().isoformat(),
                "rotation_schedule": self._get_rotation_schedule(key),
                "last_rotated": None,
                "version": 1,
            }
            
            # TODO: Store in database or external secret manager
            # For now, we'll simulate storage
            secret_id = f"secret-{project_id}-{key}-{environment}"
            
            return {
                "secret_id": secret_id,
                "key": key,
                "environment": environment,
                "created_at": secret_data["created_at"],
                "rotation_schedule": secret_data["rotation_schedule"],
                "version": secret_data["version"],
            }
            
        except Exception as e:
            raise Exception(f"Failed to store secret: {str(e)}")
    
    async def retrieve_secret(self, project_id: str, key: str, environment: str = "staging") -> Optional[str]:
        """Retrieve and decrypt a secret."""
        try:
            # TODO: Retrieve from database or external secret manager
            # For now, we'll simulate retrieval
            
            # In real implementation, this would query the database
            # and decrypt the stored value
            mock_secrets = {
                f"{project_id}-DATABASE_URL-{environment}": "postgresql://user:pass@localhost:5432/app",
                f"{project_id}-SECRET_KEY-{environment}": "super-secret-key-123",
                f"{project_id}-S3_BUCKET-{environment}": f"project-{project_id}-artifacts",
            }
            
            secret_key = f"{project_id}-{key}-{environment}"
            return mock_secrets.get(secret_key)
            
        except Exception as e:
            raise Exception(f"Failed to retrieve secret: {str(e)}")
    
    async def rotate_secret(self, project_id: str, key: str, environment: str = "staging") -> Dict[str, Any]:
        """Rotate a secret to a new value."""
        try:
            # Generate new secret value based on type
            new_value = await self._generate_new_secret_value(key)
            
            # Store the new secret
            result = await self.store_secret(project_id, key, new_value, environment)
            
            # TODO: Update applications to use new secret
            # This would involve updating environment variables,
            # restarting services, etc.
            
            return {
                **result,
                "rotated": True,
                "rotation_completed_at": datetime.utcnow().isoformat(),
                "next_rotation": self._calculate_next_rotation(key),
            }
            
        except Exception as e:
            raise Exception(f"Failed to rotate secret: {str(e)}")
    
    async def list_secrets(self, project_id: str, environment: str = "staging") -> list:
        """List all secrets for a project and environment."""
        try:
            # TODO: Query database for project secrets
            # For now, return mock data
            
            mock_secrets = [
                {
                    "key": "DATABASE_URL",
                    "environment": environment,
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_rotated": None,
                    "next_rotation": "2024-04-01T00:00:00Z",
                    "rotation_schedule": "quarterly",
                    "version": 1,
                },
                {
                    "key": "SECRET_KEY",
                    "environment": environment,
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_rotated": None,
                    "next_rotation": "2024-02-01T00:00:00Z",
                    "rotation_schedule": "monthly",
                    "version": 1,
                },
                {
                    "key": "S3_BUCKET",
                    "environment": environment,
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_rotated": None,
                    "next_rotation": None,
                    "rotation_schedule": "manual",
                    "version": 1,
                },
            ]
            
            return mock_secrets
            
        except Exception as e:
            raise Exception(f"Failed to list secrets: {str(e)}")
    
    async def delete_secret(self, project_id: str, key: str, environment: str = "staging") -> bool:
        """Delete a secret."""
        try:
            # TODO: Delete from database or external secret manager
            # For now, simulate deletion
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to delete secret: {str(e)}")
    
    async def bootstrap_project_secrets(self, project_id: str, infrastructure_outputs: Dict[str, Any], environment: str = "staging") -> Dict[str, Any]:
        """Bootstrap all secrets for a project."""
        try:
            secrets_to_create = []
            
            # Database connection string
            if "database_endpoint" in infrastructure_outputs:
                db_url = f"postgresql://app_user:secure-password-123@{infrastructure_outputs['database_endpoint']}/app"
                secrets_to_create.append(("DATABASE_URL", db_url))
            
            # S3 bucket name
            if "s3_bucket_name" in infrastructure_outputs:
                secrets_to_create.append(("S3_BUCKET", infrastructure_outputs["s3_bucket_name"]))
            
            # Redis URL
            if "redis_endpoint" in infrastructure_outputs:
                redis_url = f"redis://{infrastructure_outputs['redis_endpoint']}:6379"
                secrets_to_create.append(("REDIS_URL", redis_url))
            
            # Application secret key
            secrets_to_create.append(("SECRET_KEY", await self._generate_secret_key()))
            
            # JWT secret
            secrets_to_create.append(("JWT_SECRET", await self._generate_secret_key()))
            
            # Create all secrets
            created_secrets = []
            for key, value in secrets_to_create:
                secret_result = await self.store_secret(project_id, key, value, environment)
                created_secrets.append(secret_result)
            
            return {
                "project_id": project_id,
                "environment": environment,
                "secrets_created": len(created_secrets),
                "secrets": created_secrets,
                "bootstrap_completed_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            raise Exception(f"Failed to bootstrap secrets: {str(e)}")
    
    async def check_secret_drift(self, project_id: str, environment: str = "staging") -> Dict[str, Any]:
        """Check for secret drift and unauthorized changes."""
        try:
            secrets = await self.list_secrets(project_id, environment)
            
            drift_issues = []
            for secret in secrets:
                # Check if secret needs rotation
                if secret.get("next_rotation"):
                    next_rotation = datetime.fromisoformat(secret["next_rotation"].replace("Z", "+00:00"))
                    if datetime.utcnow().replace(tzinfo=next_rotation.tzinfo) > next_rotation:
                        drift_issues.append({
                            "key": secret["key"],
                            "issue": "rotation_overdue",
                            "severity": "medium",
                            "message": f"Secret {secret['key']} is overdue for rotation",
                        })
                
                # TODO: Check for unauthorized access or modifications
                # This would involve checking audit logs, access patterns, etc.
            
            return {
                "project_id": project_id,
                "environment": environment,
                "drift_detected": len(drift_issues) > 0,
                "issues": drift_issues,
                "checked_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            raise Exception(f"Failed to check secret drift: {str(e)}")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for secrets."""
        # In production, this should use a proper key management service
        key_material = settings.SECRET_KEY.encode()
        
        # Derive a key from the secret key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'prodsprints_salt',  # In production, use a random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        return key
    
    def _get_rotation_schedule(self, key: str) -> str:
        """Get rotation schedule for a secret type."""
        rotation_schedules = {
            "DATABASE_URL": "quarterly",
            "SECRET_KEY": "monthly",
            "JWT_SECRET": "monthly",
            "API_KEY": "monthly",
            "S3_BUCKET": "manual",
            "REDIS_URL": "quarterly",
        }
        
        return rotation_schedules.get(key, "manual")
    
    def _calculate_next_rotation(self, key: str) -> Optional[str]:
        """Calculate next rotation date for a secret."""
        schedule = self._get_rotation_schedule(key)
        
        if schedule == "manual":
            return None
        
        now = datetime.utcnow()
        
        if schedule == "monthly":
            next_rotation = now + timedelta(days=30)
        elif schedule == "quarterly":
            next_rotation = now + timedelta(days=90)
        elif schedule == "yearly":
            next_rotation = now + timedelta(days=365)
        else:
            return None
        
        return next_rotation.isoformat() + "Z"
    
    async def _generate_new_secret_value(self, key: str) -> str:
        """Generate a new secret value based on the key type."""
        if key in ["SECRET_KEY", "JWT_SECRET"]:
            return await self._generate_secret_key()
        elif key == "API_KEY":
            return await self._generate_api_key()
        else:
            # For other types, generate a random string
            return await self._generate_secret_key()
    
    async def _generate_secret_key(self) -> str:
        """Generate a secure random secret key."""
        import secrets
        return secrets.token_urlsafe(32)
    
    async def _generate_api_key(self) -> str:
        """Generate an API key."""
        import secrets
        return f"pk_{''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32))}"
