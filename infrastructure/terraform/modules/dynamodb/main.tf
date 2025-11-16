# DynamoDB Tables Module

variable "environment" {
  description = "Environment name (dev/prod)"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-trading"
}

# Trigger History Table
resource "aws_dynamodb_table" "trigger_history" {
  name           = "${var.project_name}-trigger-history-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "trigger_id"

  attribute {
    name = "trigger_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  global_secondary_index {
    name            = "TimestampIndex"
    hash_key        = "timestamp"
    projection_type = "ALL"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

# Positions Table
resource "aws_dynamodb_table" "positions" {
  name           = "${var.project_name}-positions-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "position_id"

  attribute {
    name = "position_id"
    type = "S"
  }

  attribute {
    name = "trade_date"
    type = "S"
  }

  attribute {
    name = "symbol"
    type = "S"
  }

  global_secondary_index {
    name            = "DateIndex"
    hash_key        = "trade_date"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "SymbolIndex"
    hash_key        = "symbol"
    projection_type = "ALL"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

# Economic Calendar Table
resource "aws_dynamodb_table" "economic_calendar" {
  name           = "${var.project_name}-economic-calendar-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "event_id"

  attribute {
    name = "event_id"
    type = "S"
  }

  attribute {
    name = "scheduled_time"
    type = "S"
  }

  global_secondary_index {
    name            = "ScheduleIndex"
    hash_key        = "scheduled_time"
    projection_type = "ALL"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

# Outputs
output "trigger_history_table_name" {
  value = aws_dynamodb_table.trigger_history.name
}

output "trigger_history_table_arn" {
  value = aws_dynamodb_table.trigger_history.arn
}

output "positions_table_name" {
  value = aws_dynamodb_table.positions.name
}

output "positions_table_arn" {
  value = aws_dynamodb_table.positions.arn
}

output "economic_calendar_table_name" {
  value = aws_dynamodb_table.economic_calendar.name
}

output "economic_calendar_table_arn" {
  value = aws_dynamodb_table.economic_calendar.arn
}
