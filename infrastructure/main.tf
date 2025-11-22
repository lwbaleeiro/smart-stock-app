provider "aws" {
  region = var.aws_region
}

# --- S3 Bucket (Data Lake) ---
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-data-lake-${var.environment}"
}

resource "aws_s3_bucket_acl" "data_lake_acl" {
  bucket = aws_s3_bucket.data_lake.id
  acl    = "private"
}

# --- ECR Repository (Docker Images) ---
resource "aws_ecr_repository" "api" {
  name = "${var.project_name}-api"
}

# --- RDS Instance (PostgreSQL) ---
resource "aws_db_instance" "default" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "13.4"
  instance_class       = "db.t3.micro"
  identifier           = "${var.project_name}-db-${var.environment}"
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.postgres13"
  skip_final_snapshot  = true
  publicly_accessible  = true # For MVP simplicity
}

# --- IAM Roles for Lambdas ---
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "s3_access" {
  name = "s3_access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# --- Lambda Functions ---
# Note: In a real scenario, we would zip the code and upload it.
# For Terraform validation, we'll use a dummy zip or assume it exists.
# Here we define the resources but comment out the code_source to avoid errors if file missing.

resource "aws_lambda_function" "process_handler" {
  function_name = "${var.project_name}-process-handler"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambdas.process_handler.main.handler"
  runtime       = "python3.9"
  timeout       = 300

  filename      = "lambda.zip" 
  source_code_hash = filebase64sha256("lambda.zip")

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.data_lake.id
    }
  }
}

resource "aws_lambda_function" "predict_handler" {
  function_name = "${var.project_name}-predict-handler"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambdas.predict_handler.main.handler"
  runtime       = "python3.9"
  timeout       = 900 # ML tasks take longer
  memory_size   = 1024

  filename      = "lambda.zip"
  # source_code_hash = filebase64sha256("lambda.zip")
  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.data_lake.id
      DATABASE_URL   = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.default.endpoint}/${var.project_name}"
    }
  }
  }


# --- S3 Triggers ---
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.data_lake.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.process_handler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.predict_handler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "processed/"
  }

  depends_on = [aws_lambda_permission.allow_bucket, aws_lambda_permission.allow_bucket_predict]
}

# --- App Runner (FastAPI) ---
resource "aws_iam_role" "app_runner_role" {
  name = "${var.project_name}-app-runner-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "app_runner_access" {
  role       = aws_iam_role.app_runner_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# Policy to allow App Runner to access S3
resource "aws_iam_role_policy" "app_runner_s3_access" {
  name = "app_runner_s3_access"
  role = aws_iam_role.app_runner_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_apprunner_service" "api" {
  service_name = "${var.project_name}-api"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.app_runner_role.arn
    }

    image_repository {
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          DATABASE_URL          = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.default.endpoint}/${var.project_name}"
          S3_BUCKET_NAME        = aws_s3_bucket.data_lake.id
          AWS_REGION            = var.aws_region
          # In a real scenario, use secrets manager or parameter store
        }
      }
      image_identifier      = "${aws_ecr_repository.api.repository_url}:latest"
      image_repository_type = "ECR"
    }
    auto_deployments_enabled = true
  }
  
  instance_configuration {
    instance_role_arn = aws_iam_role.app_runner_role.arn
  }

  depends_on = [aws_db_instance.default]
}
