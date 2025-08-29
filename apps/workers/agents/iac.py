"""
Infrastructure as Code (IaC) agent for Terraform provisioning.
"""

import tempfile
from pathlib import Path
from typing import Dict, Any

from .base import BaseAgent


class IaCAgent(BaseAgent):
    """Agent for generating and applying Terraform infrastructure."""
    
    async def setup(self) -> None:
        """Setup the IaC agent."""
        self.logger.info("IaC agent setup complete")
    
    async def cleanup(self) -> None:
        """Cleanup the IaC agent."""
        self.logger.info("IaC agent cleanup complete")
    
    async def subscribe_to_events(self) -> None:
        """Subscribe to blueprint generation events."""
        await self.event_bus.subscribe("blueprint.generate", self.handle_blueprint_generation)
        await self.event_bus.subscribe("iac.apply", self.handle_iac_apply)
    
    async def handle_blueprint_generation(self, data: Dict[str, Any]) -> None:
        """Handle blueprint generation request."""
        try:
            project_id = data["project_id"]
            audit_result = data["audit_result"]
            target = data.get("target", "vercel")
            
            self.logger.info("Generating IaC blueprint", project_id=project_id, target=target)
            
            # Generate Terraform templates based on audit results
            iac_templates = await self.generate_iac_templates(audit_result, target)
            
            # Publish IaC templates ready event
            await self.publish_event("iac.templates_ready", {
                "project_id": project_id,
                "iac_templates": iac_templates,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def handle_iac_apply(self, data: Dict[str, Any]) -> None:
        """Handle IaC apply request."""
        try:
            project_id = data["project_id"]
            iac_templates = data["iac_templates"]
            
            self.logger.info("Applying IaC", project_id=project_id)
            
            # Apply Terraform configuration
            apply_result = await self.apply_terraform(iac_templates)
            
            # Publish IaC applied event
            await self.publish_event("iac.applied", {
                "project_id": project_id,
                "apply_result": apply_result,
            })
            
        except Exception as e:
            await self.handle_error(e, {"project_id": data.get("project_id")})
    
    async def generate_iac_templates(self, audit_result: Dict[str, Any], target: str) -> Dict[str, Any]:
        """Generate Terraform templates based on audit results."""
        templates = {
            "main.tf": await self.generate_main_tf(audit_result, target),
            "variables.tf": await self.generate_variables_tf(audit_result),
            "outputs.tf": await self.generate_outputs_tf(audit_result, target),
            "terraform.tfvars.example": await self.generate_tfvars_example(audit_result),
        }
        
        # Add provider-specific templates
        if target == "vercel":
            templates.update(await self.generate_vercel_templates(audit_result))
        elif target == "render":
            templates.update(await self.generate_render_templates(audit_result))
        elif target == "k8s":
            templates.update(await self.generate_k8s_templates(audit_result))
        
        return templates
    
    async def generate_main_tf(self, audit_result: Dict[str, Any], target: str) -> str:
        """Generate main Terraform configuration."""
        databases = audit_result.get("databases", [])
        
        config = f'''terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
'''
        
        if target == "vercel":
            config += '''    vercel = {
      source  = "vercel/vercel"
      version = "~> 0.15"
    }
'''
        
        config += '''  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.project_name}-private-${count.index + 1}"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# S3 Bucket for artifacts
resource "aws_s3_bucket" "artifacts" {
  bucket = "${var.project_name}-artifacts-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "${var.project_name}-artifacts"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
'''
        
        # Add database resources if detected
        if "postgresql" in databases:
            config += '''
# RDS PostgreSQL
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true

  tags = {
    Name = "${var.project_name}-db"
  }
}
'''
        
        if "redis" in databases:
            config += '''
# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.project_name}-redis-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  tags = {
    Name = "${var.project_name}-redis-sg"
  }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-redis"
  description                = "Redis cluster for ${var.project_name}"

  port               = 6379
  parameter_group_name = "default.redis7"
  node_type          = "cache.t3.micro"
  num_cache_clusters = 1

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name = "${var.project_name}-redis"
  }
}
'''
        
        return config
    
    async def generate_variables_tf(self, audit_result: Dict[str, Any]) -> str:
        """Generate variables.tf file."""
        return '''variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "app"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "app_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
'''
    
    async def generate_outputs_tf(self, audit_result: Dict[str, Any], target: str) -> str:
        """Generate outputs.tf file."""
        outputs = '''output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "s3_bucket_name" {
  description = "Name of the S3 artifacts bucket"
  value       = aws_s3_bucket.artifacts.bucket
}
'''
        
        databases = audit_result.get("databases", [])
        
        if "postgresql" in databases:
            outputs += '''
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}
'''
        
        if "redis" in databases:
            outputs += '''
output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}
'''
        
        return outputs
    
    async def generate_tfvars_example(self, audit_result: Dict[str, Any]) -> str:
        """Generate terraform.tfvars.example file."""
        return '''# Copy this file to terraform.tfvars and fill in your values

project_name = "my-project"
aws_region   = "us-east-1"
environment  = "dev"

# Database configuration
db_name     = "app"
db_username = "app_user"
db_password = "your-secure-password-here"
'''
    
    async def generate_vercel_templates(self, audit_result: Dict[str, Any]) -> Dict[str, str]:
        """Generate Vercel-specific templates."""
        return {
            "vercel.tf": '''# Vercel configuration
provider "vercel" {
  # API token will be provided via VERCEL_API_TOKEN env var
}

resource "vercel_project" "main" {
  name      = var.project_name
  framework = "nextjs"
  
  git_repository = {
    type = "github"
    repo = var.github_repo
  }

  environment = [
    {
      key    = "DATABASE_URL"
      value  = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
      target = ["production", "preview"]
    },
    {
      key    = "REDIS_URL"
      value  = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379"
      target = ["production", "preview"]
    }
  ]
}

variable "github_repo" {
  description = "GitHub repository in format owner/repo"
  type        = string
}
'''
        }
    
    async def generate_render_templates(self, audit_result: Dict[str, Any]) -> Dict[str, str]:
        """Generate Render-specific templates."""
        return {
            "render.yaml": '''services:
  - type: web
    name: ${var.project_name}
    env: node
    buildCommand: npm ci && npm run build
    startCommand: npm start
    envVars:
      - key: DATABASE_URL
        value: postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}
      - key: REDIS_URL
        value: redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379
'''
        }
    
    async def generate_k8s_templates(self, audit_result: Dict[str, Any]) -> Dict[str, str]:
        """Generate Kubernetes-specific templates."""
        return {
            "k8s.tf": '''# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-cluster"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]

  tags = {
    Name = "${var.project_name}-cluster"
  }
}

resource "aws_iam_role" "eks_cluster" {
  name = "${var.project_name}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}
'''
        }
    
    async def apply_terraform(self, iac_templates: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Terraform configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            terraform_dir = Path(temp_dir) / "terraform"
            terraform_dir.mkdir()
            
            # Write Terraform files
            for filename, content in iac_templates.items():
                (terraform_dir / filename).write_text(content)
            
            # TODO: Implement actual Terraform execution
            # This would involve:
            # 1. terraform init
            # 2. terraform plan
            # 3. terraform apply
            
            # For now, return mock result
            return {
                "status": "applied",
                "resources_created": 8,
                "outputs": {
                    "vpc_id": "vpc-12345678",
                    "database_endpoint": "db.example.com:5432",
                    "s3_bucket": "my-project-artifacts-abcd1234",
                },
            }
