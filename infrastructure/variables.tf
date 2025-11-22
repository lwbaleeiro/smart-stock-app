variable "aws_region" {
  description = "AWS Region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project Name"
  default     = "quantyfy"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  default     = "dev"
}

variable "db_username" {
  description = "Database master username"
  default     = "postgres"
}

variable "db_password" {
  description = "Database master password"
  sensitive   = true
}
