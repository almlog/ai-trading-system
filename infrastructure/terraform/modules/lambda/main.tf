# Lambda Functions Module

variable "environment" {
  description = "Environment name (dev/prod)"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-trading"
}

variable "lambda_role_arn" {
  description = "IAM role ARN for Lambda execution"
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for notifications"
  type        = string
}

# Environment variables (passed from root module)
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

# News Fetch Lambda
resource "aws_lambda_function" "news_fetch" {
  filename         = "${path.module}/../../../../lambda_deployment_packages/news_fetch.zip"
  function_name    = "${var.project_name}-news-fetch-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "lambda.triggers.news_fetch.lambda_handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      ENVIRONMENT         = var.environment
      FINNHUB_API_KEY     = var.finnhub_api_key
      SNS_TOPIC_ARN       = var.sns_topic_arn
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

# Price Monitor Lambda
resource "aws_lambda_function" "price_monitor" {
  filename         = "${path.module}/../../../../lambda_deployment_packages/price_monitor.zip"
  function_name    = "${var.project_name}-price-monitor-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "lambda.triggers.price_monitor.lambda_handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      ENVIRONMENT            = var.environment
      ALPHA_VANTAGE_API_KEY  = var.alpha_vantage_api_key
      SNS_TOPIC_ARN          = var.sns_topic_arn
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

# Unified Judgment Lambda
resource "aws_lambda_function" "unified_judgment" {
  filename         = "${path.module}/../../../../lambda_deployment_packages/unified_judgment.zip"
  function_name    = "${var.project_name}-unified-judgment-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "lambda.core.unified_judgment.lambda_handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 512

  environment {
    variables = {
      ENVIRONMENT   = var.environment
      SNS_TOPIC_ARN = var.sns_topic_arn
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

# AI Analysis Lambda
resource "aws_lambda_function" "ai_analysis" {
  filename         = "${path.module}/../../../../lambda_deployment_packages/ai_analysis.zip"
  function_name    = "${var.project_name}-ai-analysis-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "lambda.core.ai_analysis.lambda_handler"
  runtime          = "python3.11"
  timeout          = 120  # Bedrock calls may take longer
  memory_size      = 512

  environment {
    variables = {
      ENVIRONMENT   = var.environment
      SNS_TOPIC_ARN = var.sns_topic_arn
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

# Outputs
output "news_fetch_function_arn" {
  value = aws_lambda_function.news_fetch.arn
}

output "price_monitor_function_arn" {
  value = aws_lambda_function.price_monitor.arn
}

output "unified_judgment_function_arn" {
  value = aws_lambda_function.unified_judgment.arn
}

output "ai_analysis_function_arn" {
  value = aws_lambda_function.ai_analysis.arn
}
