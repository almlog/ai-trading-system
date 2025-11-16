# AI Trading System - Dev Environment
# Terraform configuration for Phase 1

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use S3 backend for state management
  # backend "s3" {
  #   bucket = "ai-trading-terraform-state"
  #   key    = "dev/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AI-Trading-System"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-trading"
}

variable "finnhub_api_key" {
  description = "Finnhub API key"
  type        = string
  sensitive   = true
}

variable "alpha_vantage_api_key" {
  description = "Alpha Vantage API key"
  type        = string
  sensitive   = true
}

# DynamoDB Tables
module "dynamodb" {
  source = "../../modules/dynamodb"

  environment  = "dev"
  project_name = var.project_name
}

# S3 Buckets
module "s3" {
  source = "../../modules/s3"

  environment  = "dev"
  project_name = var.project_name
}

# SNS Topic for notifications
resource "aws_sns_topic" "trading_alerts" {
  name = "${var.project_name}-alerts-dev"

  tags = {
    Environment = "dev"
    Phase       = "1"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-execution-dev"

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

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-dev"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          module.dynamodb.trigger_history_table_arn,
          module.dynamodb.positions_table_arn,
          module.dynamodb.economic_calendar_table_arn,
          "${module.dynamodb.trigger_history_table_arn}/index/*",
          "${module.dynamodb.positions_table_arn}/index/*",
          "${module.dynamodb.economic_calendar_table_arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          module.s3.news_archive_bucket_arn,
          "${module.s3.news_archive_bucket_arn}/*",
          module.s3.pattern_library_bucket_arn,
          "${module.s3.pattern_library_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.trading_alerts.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "arn:aws:ssm:*:*:parameter/ai-trading/*"
      },
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Functions
module "lambda" {
  source = "../../modules/lambda"

  environment  = "dev"
  project_name = var.project_name

  lambda_role_arn = aws_iam_role.lambda_execution.arn
  sns_topic_arn   = aws_sns_topic.trading_alerts.arn

  finnhub_api_key       = var.finnhub_api_key
  alpha_vantage_api_key = var.alpha_vantage_api_key
}

# EventBridge Rules (Schedulers)
resource "aws_cloudwatch_event_rule" "news_fetch_schedule" {
  name                = "${var.project_name}-news-fetch-schedule-dev"
  description         = "Trigger news fetch every 5 minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "news_fetch_target" {
  rule = aws_cloudwatch_event_rule.news_fetch_schedule.name
  arn  = module.lambda.news_fetch_function_arn
}

resource "aws_lambda_permission" "allow_eventbridge_news_fetch" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.news_fetch_function_arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.news_fetch_schedule.arn
}

resource "aws_cloudwatch_event_rule" "price_monitor_schedule" {
  name                = "${var.project_name}-price-monitor-schedule-dev"
  description         = "Trigger price monitor every 1 minute"
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "price_monitor_target" {
  rule = aws_cloudwatch_event_rule.price_monitor_schedule.name
  arn  = module.lambda.price_monitor_function_arn
}

resource "aws_lambda_permission" "allow_eventbridge_price_monitor" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.price_monitor_function_arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.price_monitor_schedule.arn
}

# Outputs
output "trigger_history_table" {
  value = module.dynamodb.trigger_history_table_name
}

output "positions_table" {
  value = module.dynamodb.positions_table_name
}

output "news_archive_bucket" {
  value = module.s3.news_archive_bucket_name
}

output "sns_topic_arn" {
  value = aws_sns_topic.trading_alerts.arn
}
