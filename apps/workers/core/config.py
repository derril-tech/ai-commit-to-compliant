"""
Worker configuration.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Worker settings."""
    
    # NATS
    NATS_URL: str = Field(default="nats://localhost:4222", env="NATS_URL")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # S3/Object Storage
    S3_BUCKET: str = Field(default="prodsprints-artifacts", env="S3_BUCKET")
    S3_REGION: str = Field(default="us-east-1", env="S3_REGION")
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    
    # GitHub
    GITHUB_TOKEN: str = Field(default="", env="GITHUB_TOKEN")
    
    # Terraform
    TERRAFORM_VERSION: str = Field(default="1.6.6", env="TERRAFORM_VERSION")
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
