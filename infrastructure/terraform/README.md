# Terraform Infrastructure

AWS infrastructure for AI Trading System (Phase 1-3)

---

## 📂 Structure

```
terraform/
├── modules/               # Reusable modules
│   ├── dynamodb/         # DynamoDB tables
│   ├── s3/               # S3 buckets
│   └── lambda/           # Lambda functions
└── environments/          # Environment-specific configs
    ├── dev/              # Development environment
    │   ├── main.tf
    │   └── terraform.tfvars.example
    └── prod/             # Production environment
        ├── main.tf
        └── terraform.tfvars.example
```

---

## 🚀 Quick Start

### Prerequisites

1. **Install Terraform**
   ```bash
   # macOS
   brew install terraform

   # Windows
   choco install terraform

   # Or download from: https://www.terraform.io/downloads
   ```

2. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and region
   ```

3. **Get API Keys**
   - Finnhub: https://finnhub.io/register
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key

---

## 📋 Deployment Steps

### 1. Configure Variables

```bash
cd environments/dev

# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your API keys
nano terraform.tfvars
```

### 2. Initialize Terraform

```bash
terraform init
```

This downloads required providers and modules.

### 3. Plan Deployment

```bash
terraform plan
```

Review what resources will be created.

### 4. Apply Configuration

```bash
terraform apply
```

Type `yes` to confirm.

**Expected resources created:**
- 3 DynamoDB tables
- 2 S3 buckets
- 4 Lambda functions
- 2 EventBridge schedules
- 1 SNS topic
- IAM roles and policies

---

## 🧪 Testing Deployment

### Verify Resources

```bash
# List DynamoDB tables
aws dynamodb list-tables

# List Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `ai-trading`)].FunctionName'

# List S3 buckets
aws s3 ls | grep ai-trading
```

### Test Lambda Function

```bash
# Invoke news fetch lambda
aws lambda invoke \
  --function-name ai-trading-news-fetch-dev \
  --payload '{}' \
  response.json

cat response.json
```

---

## 📊 Cost Estimation

**Dev environment (3 months):**

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| Lambda | ~500K invocations/month | $1.00 |
| DynamoDB | On-demand, ~1M reads/writes | $2.50 |
| S3 | ~1GB storage | $0.25 |
| Bedrock | ~10K Claude Haiku requests | $3.00 |
| EventBridge | ~130K events/month | $1.00 |
| **Total** | | **~$8/month** |

---

## 🛠️ Common Operations

### Update Lambda Function

```bash
# After making code changes
cd ../../../
make phase1-package

cd infrastructure/terraform/environments/dev
terraform apply -target=module.lambda
```

### View Terraform State

```bash
terraform show
```

### Destroy All Resources

```bash
terraform destroy
```

⚠️ **WARNING**: This will delete all resources and data!

---

## 🔒 Security Best Practices

1. **Never commit terraform.tfvars**
   - Already in .gitignore
   - Contains sensitive API keys

2. **Use S3 backend for production**
   - Uncomment backend block in main.tf
   - Create S3 bucket for state storage

3. **Enable MFA for AWS account**
   ```bash
   aws iam enable-mfa-device --user-name your-user --serial-number arn:aws:iam::123456789012:mfa/user --authentication-code-1 123456 --authentication-code-2 789012
   ```

4. **Review IAM policies**
   - Lambda roles follow least privilege principle
   - Only necessary permissions granted

---

## 📖 Resources Created

### DynamoDB Tables

- **trigger_history**: Logs all trigger events for circuit breaker
- **positions**: Tracks open/closed trading positions
- **economic_calendar**: Stores scheduled economic events

### S3 Buckets

- **news-archive**: Stores fetched news data
- **pattern-library**: Stores patterns_v1.json from Phase 0

### Lambda Functions

- **news-fetch**: Fetches news from Finnhub (5min schedule)
- **price-monitor**: Monitors price volatility (1min schedule)
- **unified-judgment**: Circuit breaker and routing
- **ai-analysis**: Claude/Bedrock analysis engine

### EventBridge Rules

- **news-fetch-schedule**: Triggers every 5 minutes
- **price-monitor-schedule**: Triggers every 1 minute

---

## 🐛 Troubleshooting

### Error: "No valid credential sources found"

```bash
# Configure AWS CLI
aws configure
```

### Error: "Invalid API key"

Check your `terraform.tfvars` file has correct API keys.

### Lambda timeout errors

Increase timeout in `modules/lambda/main.tf`:

```hcl
timeout = 120  # seconds
```

---

## 📚 Next Steps

After successful deployment:

1. Upload patterns to SSM:
   ```bash
   aws ssm put-parameter \
     --name /ai-trading/patterns \
     --value file://../../../../phase0_data_analysis/outputs/patterns_v1.json \
     --type String
   ```

2. Upload prompts to SSM (create prompt files first)

3. Monitor CloudWatch Logs:
   ```bash
   aws logs tail /aws/lambda/ai-trading-news-fetch-dev --follow
   ```

4. Subscribe to SNS notifications:
   ```bash
   aws sns subscribe \
     --topic-arn <SNS_TOPIC_ARN from terraform output> \
     --protocol email \
     --notification-endpoint your-email@example.com
   ```
