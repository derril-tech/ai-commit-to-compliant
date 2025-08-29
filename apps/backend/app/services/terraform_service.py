"""
Terraform service for infrastructure provisioning.
"""

import asyncio
import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import shutil

from app.core.config import settings


class TerraformService:
    """Service for executing Terraform operations."""
    
    def __init__(self):
        self.terraform_version = "1.6.6"
    
    async def apply_infrastructure(self, project_id: str, iac_templates: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Terraform infrastructure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            terraform_dir = Path(temp_dir) / "terraform"
            terraform_dir.mkdir()
            
            try:
                # Write Terraform files
                await self._write_terraform_files(terraform_dir, iac_templates)
                
                # Write variables file
                await self._write_variables_file(terraform_dir, variables)
                
                # Initialize Terraform
                init_result = await self._run_terraform_command(terraform_dir, ["init"])
                if not init_result["success"]:
                    return {"status": "failed", "stage": "init", "error": init_result["error"]}
                
                # Plan Terraform
                plan_result = await self._run_terraform_command(terraform_dir, ["plan", "-out=tfplan"])
                if not plan_result["success"]:
                    return {"status": "failed", "stage": "plan", "error": plan_result["error"]}
                
                # Apply Terraform
                apply_result = await self._run_terraform_command(terraform_dir, ["apply", "-auto-approve", "tfplan"])
                if not apply_result["success"]:
                    return {"status": "failed", "stage": "apply", "error": apply_result["error"]}
                
                # Get outputs
                outputs_result = await self._run_terraform_command(terraform_dir, ["output", "-json"])
                outputs = json.loads(outputs_result["output"]) if outputs_result["success"] else {}
                
                # Get state for resource tracking
                state_result = await self._run_terraform_command(terraform_dir, ["show", "-json"])
                state_data = json.loads(state_result["output"]) if state_result["success"] else {}
                
                return {
                    "status": "completed",
                    "resources_created": len(state_data.get("values", {}).get("root_module", {}).get("resources", [])),
                    "outputs": outputs,
                    "state_summary": self._extract_state_summary(state_data),
                    "duration_seconds": apply_result.get("duration", 0),
                    "terraform_version": self.terraform_version,
                }
                
            except Exception as e:
                return {
                    "status": "failed",
                    "stage": "execution",
                    "error": str(e)
                }
    
    async def plan_infrastructure(self, project_id: str, iac_templates: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Plan Terraform infrastructure changes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            terraform_dir = Path(temp_dir) / "terraform"
            terraform_dir.mkdir()
            
            try:
                # Write Terraform files
                await self._write_terraform_files(terraform_dir, iac_templates)
                
                # Write variables file
                await self._write_variables_file(terraform_dir, variables)
                
                # Initialize Terraform
                init_result = await self._run_terraform_command(terraform_dir, ["init"])
                if not init_result["success"]:
                    return {"status": "failed", "stage": "init", "error": init_result["error"]}
                
                # Plan Terraform
                plan_result = await self._run_terraform_command(terraform_dir, ["plan", "-json"])
                if not plan_result["success"]:
                    return {"status": "failed", "stage": "plan", "error": plan_result["error"]}
                
                # Parse plan output
                plan_data = self._parse_plan_output(plan_result["output"])
                
                return {
                    "status": "completed",
                    "plan_data": plan_data,
                    "resources_to_add": plan_data.get("resource_changes", {}).get("add", 0),
                    "resources_to_change": plan_data.get("resource_changes", {}).get("change", 0),
                    "resources_to_destroy": plan_data.get("resource_changes", {}).get("destroy", 0),
                    "estimated_cost": await self._estimate_plan_cost(plan_data),
                }
                
            except Exception as e:
                return {
                    "status": "failed",
                    "stage": "planning",
                    "error": str(e)
                }
    
    async def destroy_infrastructure(self, project_id: str, iac_templates: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Destroy Terraform infrastructure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            terraform_dir = Path(temp_dir) / "terraform"
            terraform_dir.mkdir()
            
            try:
                # Write Terraform files
                await self._write_terraform_files(terraform_dir, iac_templates)
                
                # Write variables file
                await self._write_variables_file(terraform_dir, variables)
                
                # Initialize Terraform
                init_result = await self._run_terraform_command(terraform_dir, ["init"])
                if not init_result["success"]:
                    return {"status": "failed", "stage": "init", "error": init_result["error"]}
                
                # Destroy infrastructure
                destroy_result = await self._run_terraform_command(terraform_dir, ["destroy", "-auto-approve"])
                if not destroy_result["success"]:
                    return {"status": "failed", "stage": "destroy", "error": destroy_result["error"]}
                
                return {
                    "status": "completed",
                    "resources_destroyed": destroy_result.get("resources_destroyed", 0),
                    "duration_seconds": destroy_result.get("duration", 0),
                }
                
            except Exception as e:
                return {
                    "status": "failed",
                    "stage": "destruction",
                    "error": str(e)
                }
    
    async def validate_templates(self, iac_templates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Terraform templates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            terraform_dir = Path(temp_dir) / "terraform"
            terraform_dir.mkdir()
            
            try:
                # Write Terraform files
                await self._write_terraform_files(terraform_dir, iac_templates)
                
                # Initialize Terraform
                init_result = await self._run_terraform_command(terraform_dir, ["init"])
                if not init_result["success"]:
                    return {"valid": False, "errors": [init_result["error"]]}
                
                # Validate Terraform
                validate_result = await self._run_terraform_command(terraform_dir, ["validate", "-json"])
                if not validate_result["success"]:
                    return {"valid": False, "errors": [validate_result["error"]]}
                
                validation_data = json.loads(validate_result["output"])
                
                return {
                    "valid": validation_data.get("valid", False),
                    "errors": validation_data.get("error_count", 0),
                    "warnings": validation_data.get("warning_count", 0),
                    "diagnostics": validation_data.get("diagnostics", []),
                }
                
            except Exception as e:
                return {
                    "valid": False,
                    "errors": [str(e)]
                }
    
    async def get_terraform_version(self) -> str:
        """Get Terraform version."""
        try:
            result = await self._run_command(["terraform", "version", "-json"])
            if result["success"]:
                version_data = json.loads(result["output"])
                return version_data.get("terraform_version", "unknown")
            return "unknown"
        except Exception:
            return "unknown"
    
    async def _write_terraform_files(self, terraform_dir: Path, iac_templates: Dict[str, Any]) -> None:
        """Write Terraform files to directory."""
        resources = iac_templates.get("resources", [])
        providers = iac_templates.get("providers", [])
        
        # Write main.tf
        main_tf_content = self._generate_main_tf(resources, providers)
        (terraform_dir / "main.tf").write_text(main_tf_content)
        
        # Write variables.tf
        variables_tf_content = self._generate_variables_tf()
        (terraform_dir / "variables.tf").write_text(variables_tf_content)
        
        # Write outputs.tf
        outputs_tf_content = self._generate_outputs_tf(resources)
        (terraform_dir / "outputs.tf").write_text(outputs_tf_content)
        
        # Write versions.tf
        versions_tf_content = self._generate_versions_tf(providers)
        (terraform_dir / "versions.tf").write_text(versions_tf_content)
    
    async def _write_variables_file(self, terraform_dir: Path, variables: Dict[str, Any]) -> None:
        """Write terraform.tfvars file."""
        tfvars_content = ""
        for key, value in variables.items():
            if isinstance(value, str):
                tfvars_content += f'{key} = "{value}"\n'
            elif isinstance(value, bool):
                tfvars_content += f'{key} = {str(value).lower()}\n'
            elif isinstance(value, (int, float)):
                tfvars_content += f'{key} = {value}\n'
            elif isinstance(value, list):
                tfvars_content += f'{key} = {json.dumps(value)}\n'
            elif isinstance(value, dict):
                tfvars_content += f'{key} = {json.dumps(value)}\n'
        
        (terraform_dir / "terraform.tfvars").write_text(tfvars_content)
    
    async def _run_terraform_command(self, terraform_dir: Path, args: list) -> Dict[str, Any]:
        """Run Terraform command."""
        return await self._run_command(["terraform"] + args, cwd=terraform_dir)
    
    async def _run_command(self, args: list, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run shell command asynchronously."""
        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "TF_IN_AUTOMATION": "1", "TF_INPUT": "0"}
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "output": stdout.decode(),
                "error": stderr.decode(),
                "return_code": process.returncode,
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "return_code": -1,
            }
    
    def _generate_main_tf(self, resources: list, providers: list) -> str:
        """Generate main.tf content."""
        content = "# Generated Terraform configuration\n\n"
        
        # Add providers
        for provider in providers:
            content += f'''provider "{provider['name']}" {{
  version = "{provider['version']}"
}}

'''
        
        # Add resources
        for resource in resources:
            resource_type = resource["type"]
            resource_name = resource["name"]
            
            content += f'resource "{resource_type}" "{resource_name}" {{\n'
            
            # Add resource configuration based on type
            if resource_type == "aws_vpc":
                content += '  cidr_block           = "10.0.0.0/16"\n'
                content += '  enable_dns_hostnames = true\n'
                content += '  enable_dns_support   = true\n'
                content += f'  tags = {{\n    Name = "${{var.project_name}}-vpc"\n  }}\n'
            
            elif resource_type == "aws_s3_bucket":
                content += f'  bucket = "${{var.project_name}}-artifacts-${{random_id.bucket_suffix.hex}}"\n'
                content += f'  tags = {{\n    Name = "${{var.project_name}}-artifacts"\n  }}\n'
            
            elif resource_type == "aws_db_instance":
                content += '  identifier = "${var.project_name}-db"\n'
                content += '  engine = "postgres"\n'
                content += '  engine_version = "15.4"\n'
                content += '  instance_class = "db.t3.micro"\n'
                content += '  allocated_storage = 20\n'
                content += '  storage_encrypted = true\n'
                content += '  db_name = var.db_name\n'
                content += '  username = var.db_username\n'
                content += '  password = var.db_password\n'
                content += '  skip_final_snapshot = true\n'
            
            elif resource_type == "random_id":
                content += '  byte_length = 4\n'
            
            content += "}\n\n"
        
        return content
    
    def _generate_variables_tf(self) -> str:
        """Generate variables.tf content."""
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
    
    def _generate_outputs_tf(self, resources: list) -> str:
        """Generate outputs.tf content."""
        content = "# Terraform outputs\n\n"
        
        for resource in resources:
            if resource["type"] == "aws_vpc":
                content += f'''output "vpc_id" {{
  description = "ID of the VPC"
  value       = aws_vpc.{resource["name"]}.id
}}

'''
            elif resource["type"] == "aws_s3_bucket":
                content += f'''output "s3_bucket_name" {{
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.{resource["name"]}.bucket
}}

'''
            elif resource["type"] == "aws_db_instance":
                content += f'''output "database_endpoint" {{
  description = "Database endpoint"
  value       = aws_db_instance.{resource["name"]}.endpoint
  sensitive   = true
}}

'''
        
        return content
    
    def _generate_versions_tf(self, providers: list) -> str:
        """Generate versions.tf content."""
        content = '''terraform {
  required_version = ">= 1.0"
  required_providers {
'''
        
        for provider in providers:
            content += f'''    {provider["name"]} = {{
      source  = "hashicorp/{provider["name"]}"
      version = "{provider["version"]}"
    }}
'''
        
        content += '''  }
}
'''
        
        return content
    
    def _parse_plan_output(self, plan_output: str) -> Dict[str, Any]:
        """Parse Terraform plan JSON output."""
        try:
            lines = plan_output.strip().split('\n')
            plan_data = {"resource_changes": {"add": 0, "change": 0, "destroy": 0}}
            
            for line in lines:
                if line.strip().startswith('{"'):
                    try:
                        data = json.loads(line)
                        if data.get("type") == "resource_drift":
                            continue
                        elif data.get("type") == "planned_change":
                            change = data.get("change", {})
                            actions = change.get("actions", [])
                            if "create" in actions:
                                plan_data["resource_changes"]["add"] += 1
                            elif "update" in actions:
                                plan_data["resource_changes"]["change"] += 1
                            elif "delete" in actions:
                                plan_data["resource_changes"]["destroy"] += 1
                    except json.JSONDecodeError:
                        continue
            
            return plan_data
            
        except Exception:
            return {"resource_changes": {"add": 0, "change": 0, "destroy": 0}}
    
    def _extract_state_summary(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary from Terraform state."""
        try:
            resources = state_data.get("values", {}).get("root_module", {}).get("resources", [])
            
            resource_types = {}
            for resource in resources:
                resource_type = resource.get("type", "unknown")
                resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
            
            return {
                "total_resources": len(resources),
                "resource_types": resource_types,
                "terraform_version": state_data.get("terraform_version", "unknown"),
            }
            
        except Exception:
            return {"total_resources": 0, "resource_types": {}}
    
    async def _estimate_plan_cost(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate cost for planned resources."""
        # Simple cost estimation based on resource counts
        resource_changes = plan_data.get("resource_changes", {})
        
        estimated_monthly_cost = 0
        cost_breakdown = {}
        
        # Basic cost estimates (simplified)
        add_count = resource_changes.get("add", 0)
        if add_count > 0:
            estimated_monthly_cost += add_count * 10  # $10 per resource average
            cost_breakdown["new_resources"] = add_count * 10
        
        return {
            "estimated_monthly_cost": estimated_monthly_cost,
            "cost_breakdown": cost_breakdown,
            "currency": "USD",
            "confidence": "low",
            "note": "Estimates are rough approximations"
        }
