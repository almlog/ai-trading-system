# セットアップガイド

AI株式ニュース分析・自動取引システムの環境構築手順

---

## 📋 前提条件

### 必須ツール

- **Python 3.11+**
- **Git**
- **AWS CLI** (Phase 1以降)
- **Terraform 1.5+** (Phase 1以降)

### APIキー取得（Phase 0から必要）

1. **Kaggle API**
   - https://www.kaggle.com/account にアクセス
   - "Create New API Token" をクリック
   - `kaggle.json` をダウンロード

2. **Anthropic API (Claude)**
   - https://console.anthropic.com/ にアクセス
   - APIキーを生成

3. **Finnhub API** (Phase 1以降)
   - https://finnhub.io/register
   - 無料枠でOK

4. **Alpha Vantage API** (Phase 1以降)
   - https://www.alphavantage.co/support/#api-key
   - 無料枠でOK

---

## 🚀 Phase 0: データ分析環境のセットアップ

### 1. リポジトリのクローン（または初期化）

```bash
# 新規作成の場合
mkdir ai-trading-system
cd ai-trading-system

# または、既存リポジトリのクローン
git clone <your-repo-url>
cd ai-trading-system
```

### 2. Python仮想環境の作成

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージのインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# エディタで編集
notepad .env  # Windows
nano .env     # Mac/Linux
```

**必須の環境変数（Phase 0）:**
```
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 5. Kaggle API設定

```bash
# Windows
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# Mac/Linux
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 6. Phase 0のセットアップ実行

```bash
make phase0-setup
```

これで以下が完了します：
- NLTKデータのダウンロード
- 必要なPythonパッケージの確認

### 7. Kaggleデータのダウンロード

```bash
make phase0-download-data
```

### 8. データ分析の開始

```bash
# Option A: Jupyter Notebookで対話的に分析
make phase0-notebook

# Option B: スクリプトで自動実行
make phase0-analyze
```

### 9. パターンの検証

```bash
make phase0-validate
```

---

## 🚀 Phase 1: AWS環境のセットアップ

### 1. AWS CLIの設定

```bash
aws configure
```

入力項目：
- AWS Access Key ID
- AWS Secret Access Key
- Default region (推奨: us-east-1)
- Default output format (json)

### 2. Terraformの初期化

```bash
cd infrastructure/terraform/environments/dev

# terraform.tfvarsファイルの作成
cp terraform.tfvars.example terraform.tfvars

# APIキーを編集
notepad terraform.tfvars  # Windows
nano terraform.tfvars     # Mac/Linux
```

**terraform.tfvarsの内容:**
```hcl
aws_region = "us-east-1"
project_name = "ai-trading"

finnhub_api_key       = "your_finnhub_key"
alpha_vantage_api_key = "your_alpha_vantage_key"
```

### 3. Terraformの実行

```bash
# 初期化
terraform init

# プラン確認
terraform plan

# デプロイ
terraform apply
```

### 4. パターンのアップロード

Phase 0で生成した `patterns_v1.json` をSSM Parameter Storeにアップロード：

```bash
cd ../../../..  # プロジェクトルートに戻る

aws ssm put-parameter \
  --name /ai-trading/patterns \
  --value file://phase0_data_analysis/outputs/patterns_v1.json \
  --type String \
  --description "Phase 0で発見したパターン"
```

### 5. SNS通知の設定（オプション）

```bash
# Terraform出力からSNS Topic ARNを取得
cd infrastructure/terraform/environments/dev
terraform output sns_topic_arn

# メール通知を購読
aws sns subscribe \
  --topic-arn <SNS_TOPIC_ARN> \
  --protocol email \
  --notification-endpoint your-email@example.com

# 確認メールのリンクをクリック
```

### 6. 動作確認

```bash
# Lambda関数のテスト実行
aws lambda invoke \
  --function-name ai-trading-news-fetch-dev \
  --payload '{}' \
  response.json

cat response.json

# ログの確認
make lambda-logs FUNCTION=news_fetch_lambda
```

---

## 🚀 Phase 2: 生データ分析

### 1. Phase 2スクリプトの実行

```bash
# Phase 0と同じデータを使用
make phase2-analyze-raw
```

### 2. A案とB案の比較

```bash
make phase2-compare
```

### 3. 比較レポートの確認

```bash
cat claudedocs/phase2_ab_comparison_report.md
```

---

## 🚀 Phase 3: 統合と最終評価

### 1. 日次評価の実行（手動）

```bash
python scripts/daily_performance_evaluator.py
```

### 2. 最終レポートの生成

```bash
make phase3-generate-report
```

### 3. レポートの確認

```bash
cat claudedocs/final_research_report.md
```

---

## 🔍 トラブルシューティング

### Python関連

**エラー: "No module named 'XXX'"**
```bash
# 仮想環境が有効化されているか確認
which python  # Mac/Linux
where python  # Windows

# 依存パッケージの再インストール
pip install -r requirements.txt
```

### Kaggle関連

**エラー: "Kaggle credentials not found"**
```bash
# kaggle.jsonの配置場所を確認
# Windows: C:\Users\<username>\.kaggle\kaggle.json
# Mac/Linux: ~/.kaggle/kaggle.json
```

### AWS関連

**エラー: "Unable to locate credentials"**
```bash
# AWS CLIの設定を確認
aws configure list

# 必要に応じて再設定
aws configure
```

**エラー: "Access Denied"**
- IAMユーザーに適切な権限があるか確認
- 必要な権限: Lambda, DynamoDB, S3, Bedrock, EventBridge, SNS, SSM

### Terraform関連

**エラー: "Resource already exists"**
```bash
# 既存リソースをインポート（該当する場合）
terraform import <resource_type>.<resource_name> <resource_id>

# または、state を削除して再作成
terraform state rm <resource_type>.<resource_name>
```

---

## 📊 よく使うコマンド

```bash
# Phase 0
make phase0-notebook              # Jupyter起動
make phase0-analyze               # パターン発見
make phase0-validate              # パターン検証

# Phase 1
make phase1-test-local            # ローカルテスト
make phase1-deploy-dev            # Dev環境デプロイ
make lambda-logs FUNCTION=<name>  # ログ確認

# Phase 2
make phase2-analyze-raw           # 生データ分析
make phase2-compare               # パターン比較

# Phase 3
make phase3-evaluate-daily        # 日次評価
make phase3-generate-report       # 最終レポート

# 共通
make aws-costs                    # AWS料金確認
make clean                        # 一時ファイル削除
make help                         # 全コマンド一覧
```

---

## 🎓 学習リソース

### 技術ドキュメント

- **設計書**: [docs/DESIGN_DOC_FINAL.md](docs/DESIGN_DOC_FINAL.md)
- **Lambda README**: [lambda/README.md](lambda/README.md)
- **Terraform README**: [infrastructure/terraform/README.md](infrastructure/terraform/README.md)
- **Phase 0 README**: [phase0_data_analysis/README.md](phase0_data_analysis/README.md)

### 外部リソース

- **AWS Lambda**: https://docs.aws.amazon.com/lambda/
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/
- **Terraform**: https://www.terraform.io/docs
- **Finnhub API**: https://finnhub.io/docs/api
- **Alpha Vantage API**: https://www.alphavantage.co/documentation/

---

## ✅ セットアップ完了チェックリスト

### Phase 0
- [ ] Python仮想環境が動作している
- [ ] `.env` ファイルにAPIキーを設定済み
- [ ] Kaggle APIが動作確認済み
- [ ] `patterns_v1.json` が生成されている

### Phase 1
- [ ] AWS CLIが設定済み
- [ ] Terraform でインフラをデプロイ済み
- [ ] Lambda関数が実行可能
- [ ] SSM にパターンをアップロード済み

### Phase 2
- [ ] `patterns_v2_raw.json` が生成されている
- [ ] A案とB案の比較レポートが生成されている

### Phase 3
- [ ] 日次評価が実行可能
- [ ] 最終レポートが生成されている

---

## 🙋 サポート

問題が解決しない場合：

1. エラーメッセージをコピー
2. GitHubのIssueを作成（またはプロジェクト管理者に連絡）
3. 以下の情報を含める：
   - OS（Windows/Mac/Linux）
   - Pythonバージョン（`python --version`）
   - エラーメッセージ全文
   - 実行したコマンド

---

**セットアップ完了！　Phase 0から開始してください。**
