output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.data_lake.id
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.api.repository_url
}

output "db_endpoint" {
  description = "RDS Endpoint"
  value       = aws_db_instance.default.endpoint
}

output "api_url" {
  description = "URL of the App Runner service"
  value       = aws_apprunner_service.api.service_url
}
