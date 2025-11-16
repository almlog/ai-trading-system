# Lambda Functions

Phase 1-3のAWS Lambda関数群

---

## 📂 Directory Structure

```
lambda/
├── triggers/          # トリガー系Lambda
│   ├── news_fetch.py          # Pattern A: ニュース取得
│   ├── price_monitor.py       # Pattern B: ボラティリティ監視
│   └── calendar_checker.py    # Pattern C: 経済指標スケジュール
├── core/              # コアロジック
│   ├── unified_judgment.py    # 統合判断（サーキットブレーカー）
│   ├── ai_analysis.py         # AI分析エンジン
│   └── position_manager.py    # ポジション管理・取引実行
├── evaluation/        # 評価系
│   └── daily_evaluator.py     # 日次パフォーマンス評価
├── utils/             # ユーティリティ
│   ├── constants.py           # 定数
│   ├── aws_clients.py         # AWSクライアント
│   └── circuit_breaker.py     # サーキットブレーカー
└── tests/             # テスト
    └── test_circuit_breaker.py
```

---

## 🔄 Lambda Invocation Flow

```
[EventBridge Scheduler]
  ├─ news_fetch_lambda (5min)
  ├─ price_monitor_lambda (1min)
  └─ calendar_checker_lambda (15min)
        │
        ▼
  [EventBridge Custom Events]
        │
        ▼
  unified_judgment_lambda
    ├─ Circuit Breaker Check
    └─ Delegate to AI
        │
        ▼
  ai_analysis_lambda
    ├─ Load patterns (SSM)
    ├─ Invoke Bedrock
    └─ Decide action
        │
        ▼
  position_manager_lambda (if action recommended)
    ├─ Execute trade
    └─ Save to DynamoDB
```

---

## 🚀 Deployment

### Package Lambda

```bash
make phase1-package
```

### Deploy with Terraform

```bash
# Dev environment
make phase1-deploy-dev

# Production (careful!)
make phase1-deploy-prod
```

---

## 🧪 Testing

### Local Testing

```bash
# Run unit tests
make phase1-test-local

# Test specific function
pytest lambda/tests/test_circuit_breaker.py -v
```

### Manual Invocation

```bash
# Invoke Lambda directly
aws lambda invoke \
  --function-name ai-trading-news-fetch \
  --payload '{}' \
  response.json
```

---

## 📊 Monitoring

### View Logs

```bash
# View logs for specific function
make lambda-logs FUNCTION=news_fetch_lambda

# Follow logs in real-time
aws logs tail /aws/lambda/ai-trading-news-fetch --follow
```

### Check Metrics

```bash
# CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=ai-trading-news-fetch \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

---

## 🔒 Environment Variables

Each Lambda function requires these environment variables (set via Terraform):

- `FINNHUB_API_KEY`: Finnhub API key
- `ALPHA_VANTAGE_API_KEY`: Alpha Vantage API key
- `ANTHROPIC_API_KEY`: Anthropic API key (if not using Bedrock)
- `SNS_TOPIC_ARN`: SNS topic for notifications
- `ENVIRONMENT`: dev/prod

---

## 📖 Next Steps

After Lambda functions are deployed:

1. Upload patterns to SSM: `aws ssm put-parameter --name /ai-trading/patterns --value file://patterns_v1.json`
2. Upload prompts to SSM
3. Enable EventBridge schedules
4. Monitor CloudWatch logs
