# S3 Buckets Module

variable "environment" {
  description = "Environment name (dev/prod)"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-trading"
}

# News Archive Bucket
resource "aws_s3_bucket" "news_archive" {
  bucket = "${var.project_name}-news-archive-${var.environment}"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "1"
  }
}

resource "aws_s3_bucket_versioning" "news_archive" {
  bucket = aws_s3_bucket.news_archive.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "news_archive" {
  bucket = aws_s3_bucket.news_archive.id

  rule {
    id     = "delete-old-news"
    status = "Enabled"

    expiration {
      days = 90  # Keep news for 90 days
    }
  }
}

# Pattern Library Bucket
resource "aws_s3_bucket" "pattern_library" {
  bucket = "${var.project_name}-pattern-library-${var.environment}"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Phase       = "0-1"
  }
}

resource "aws_s3_bucket_versioning" "pattern_library" {
  bucket = aws_s3_bucket.pattern_library.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Outputs
output "news_archive_bucket_name" {
  value = aws_s3_bucket.news_archive.bucket
}

output "news_archive_bucket_arn" {
  value = aws_s3_bucket.news_archive.arn
}

output "pattern_library_bucket_name" {
  value = aws_s3_bucket.pattern_library.bucket
}

output "pattern_library_bucket_arn" {
  value = aws_s3_bucket.pattern_library.arn
}
