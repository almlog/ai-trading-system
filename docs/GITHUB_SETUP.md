# GitHub リポジトリ作成ガイド

このプロジェクトをGitHubで管理するための手順

---

## 🎯 目的

- コードのバージョン管理
- Phase毎のマイルストーン管理
- 将来的な公開（ポートフォリオとして）
- バックアップ

---

## 📋 事前準備

### 1. GitHubアカウント

すでにアカウントをお持ちの場合はスキップ。

- https://github.com/signup

### 2. Git設定

ローカルのGit設定を確認：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🚀 リポジトリ作成手順

### Step 1: GitHubでリポジトリ作成

1. GitHubにログイン
2. 右上の "+" → "New repository"
3. 以下を入力：

**Repository name**: `ai-trading-system` (または任意の名前)

**Description**:
```
AI-powered news analysis and automated trading system for US stocks.
Built with AWS Lambda, Bedrock (Claude), and Terraform.
```

**Visibility**:
- **Private** (Phase 0-3完了まで非公開推奨)
- Public (Phase 3完了後に公開を検討)

**Initialize repository**:
- ❌ Add a README file (すでにローカルにある)
- ❌ Add .gitignore (すでにローカルにある)
- ✅ Choose a license: MIT License (推奨)

4. "Create repository" をクリック

---

### Step 2: ローカルリポジトリをGitHubに接続

GitHubが表示する "…or push an existing repository from the command line" の手順に従う：

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/ai-trading-system.git

# または SSH を使用する場合
git remote add origin git@github.com:YOUR_USERNAME/ai-trading-system.git

# ブランチ名をmainに変更（必要に応じて）
git branch -M main

# 初回プッシュ
git push -u origin main
```

---

### Step 3: GitHub Actions（オプション）

Phase 1以降、CI/CDを設定する場合：

`.github/workflows/ci.yml` を作成（別途設定）

---

## 📊 ブランチ戦略

### メインブランチ

- **main**: 安定版（Phase完了時にマージ）
- **develop**: 開発中（日々のコミット）

### フィーチャーブランチ

各Phase用にブランチを切る：

```bash
# Phase 0開始時
git checkout -b feature/phase0-pattern-discovery

# 作業完了後
git checkout main
git merge feature/phase0-pattern-discovery
git push origin main
```

---

## 🏷️ タグ付け

Phase完了時にタグを付ける：

```bash
# Phase 0完了時
git tag -a v0.1.0 -m "Phase 0: Pattern Discovery Complete"
git push origin v0.1.0

# Phase 1完了時
git tag -a v1.0.0 -m "Phase 1: Autonomous Trading System Complete"
git push origin v1.0.0
```

---

## 📝 コミットメッセージ規約

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードフォーマット
- `refactor`: リファクタリング
- `test`: テスト追加
- `chore`: ビルド・設定変更

### Examples

```bash
git commit -m "feat(phase0): add Kaggle data download script"
git commit -m "fix(lambda): resolve DynamoDB timeout issue"
git commit -m "docs(readme): update setup guide"
```

---

## 🔒 セキュリティ

### 絶対にコミットしてはいけないファイル

`.gitignore` に含まれていることを確認：

- `.env` (API keys)
- `terraform.tfvars` (AWS credentials)
- `kaggle.json` (Kaggle API key)
- `*.key`, `*.pem` (秘密鍵)

### 確認方法

```bash
# .gitignore が機能しているか確認
git status

# 除外されているか確認
git check-ignore .env
```

---

## 📋 Issue管理

### Issue Template

GitHubのIssueで各Phaseのタスクを管理：

**Phase 0 Issue例**:
```
Title: [Phase 0] Kaggleデータセットのダウンロード

**Task**
- [ ] データセット候補のリストアップ
- [ ] ダウンロードスクリプトの実装
- [ ] データ品質の確認

**Acceptance Criteria**
- データが`phase0_data_analysis/data/`に保存されている
- 過去1-2年分のデータが揃っている
- README更新済み
```

---

## 🎯 Milestone設定

各PhaseをMilestoneとして設定：

1. **Milestone 1**: Phase 0 - Pattern Discovery
2. **Milestone 2**: Phase 1 - Autonomous System
3. **Milestone 3**: Phase 2 - Raw Data Analysis
4. **Milestone 4**: Phase 3 - Final Report

---

## 📖 README Badge

GitHub READMEにバッジを追加（Phase 1以降）：

```markdown
![Phase](https://img.shields.io/badge/Phase-0%20Complete-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20Bedrock-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
```

---

## 🌐 Phase 3後の公開準備

Phase 3完了後、リポジトリを公開する場合：

### 1. セキュリティチェック

```bash
# 秘密情報が含まれていないか確認
git log --all --full-history --source -- "*.env" "*.key"
```

### 2. README更新

- プロジェクト概要
- デモ動画・スクリーンショット
- セットアップ手順
- ライセンス情報

### 3. 公開設定変更

GitHub Settings → Danger Zone → Change visibility → Public

---

## 🔄 定期的な作業

### Daily

```bash
# 作業開始時
git pull origin main

# 作業中（こまめにコミット）
git add .
git commit -m "feat(phase0): implement feature extraction"

# 作業終了時
git push origin main
```

### Weekly

- Issueのステータス更新
- Milestoneの進捗確認
- 不要なブランチの削除

---

## 🆘 トラブルシューティング

### プッシュできない

```bash
# リモートの変更を取得してマージ
git pull origin main --rebase
git push origin main
```

### 間違えてコミットした

```bash
# 直前のコミットを取り消し（ローカルのみ）
git reset --soft HEAD^

# プッシュ済みの場合は新しいコミットで修正
git revert HEAD
```

### .gitignore が効かない

```bash
# キャッシュをクリア
git rm -r --cached .
git add .
git commit -m "fix: update .gitignore"
```

---

## 📚 参考リソース

- [GitHub Docs](https://docs.github.com/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**GitHubでプロジェクトを管理しましょう！** 🚀
