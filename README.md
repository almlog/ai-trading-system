# AI News Analysis & Automated Trading System
## 米国株式ニュース分析・自動取引システム

**プロジェクト期間:** 3ヶ月（2025年11月〜2026年1月）  
**予算:** 50,000円  
**目的:** AI研究とニュース分析スキルの習得

---

## 📋 プロジェクト概要

育児休暇中の3ヶ月を活用し、AIによる米国株式ニュース分析システムを構築する研究プロジェクト。

### 主要な目標

1. **AI研究:** Claude/Geminiを活用したプロンプト設計と継続的改善
2. **スキル習得:** 金融ニュース分析、AWSサーバーレス実装
3. **パターン発見:** AIが市場の「黄金パターン」を発見

### 投資対象

- **市場:** 米国株式
- **銘柄:** テック大手5社（AAPL, MSFT, GOOGL, AMZN, NVDA）

---

## 🗺️ 4フェーズロードマップ

| Phase | 期間 | 目標 | 成果物 |
|-------|------|------|--------|
| **Phase 0** | Week 1-2 | Kaggleデータでパターン発見（A案） | `patterns_v1.json` |
| **Phase 1** | Week 3 - Month 2 | リアルタイム自動取引システム構築 | 稼働システム |
| **Phase 2** | Month 2後半 - Month 3前半 | 生データ分析でパターン精緻化（B案） | `patterns_v2_raw.json` |
| **Phase 3** | Month 3後半 | 統合と研究成果まとめ | 最終研究レポート |

---

## 🏗️ システムアーキテクチャ

### トリガー方式

3つのイベント駆動型トリガー：

1. **ニュース発生時:** Finnhub APIから5分ごとに新規ニュース取得
2. **ボラティリティ監視:** 株価が±2%以上急変動したら検知
3. **経済指標スケジュール:** FOMC等の重要イベント30分前/直後に起動

### 技術スタック

- **クラウド:** AWS（Lambda, S3, DynamoDB, EventBridge, Bedrock）
- **AI:** Claude 3 Haiku（プロンプトベースの分析）
- **データソース:** Finnhub, Alpha Vantage（無料枠）
- **IaC:** Terraform
- **言語:** Python 3.11

---

## 🚀 クイックスタート

### 前提条件

- Python 3.11+
- AWS CLI設定済み
- Kaggle APIキー（Phase 0用）
- Finnhub/Alpha Vantage APIキー（Phase 1以降）

### セットアップ

```bash
# 1. リポジトリクローン（または新規作成）
git clone <your-repo-url>
cd ai-trading-system

# 2. Python仮想環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存パッケージインストール
make phase0-setup

# 4. 環境変数設定
cp .env.example .env
# .env を編集してAPIキーを設定

# 5. Kaggle API設定
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Phase 0: データ分析を始める

```bash
# Kaggleデータセットをダウンロード
make phase0-download-data

# Jupyter Notebookを起動
make phase0-notebook
```

---

## 📂 プロジェクト構造

```
ai-trading-system/
├── docs/                          # ドキュメント
│   └── DESIGN_DOC_FINAL.md       # 完全設計書
├── phase0_data_analysis/          # Phase 0: データ分析
│   ├── notebooks/                 # Jupyter Notebook
│   └── outputs/
│       └── patterns_v1.json      # 発見したパターン
├── lambda/                        # Lambda関数（Phase 1-3）
│   ├── triggers/                  # トリガー系
│   ├── core/                      # コアロジック
│   └── evaluation/                # 評価系
├── infrastructure/                # IaC
│   └── terraform/
├── config/                        # 設定ファイル
│   ├── patterns/
│   └── economic_calendar.json
└── Makefile                      # よく使うコマンド集
```

---

## 💰 予算配分

| 費目 | 金額 |
|------|------|
| 証券口座証拠金 | 20,000円 |
| AWS利用料（3ヶ月） | 10,000円 |
| 予備費 | 20,000円 |
| **合計** | **50,000円** |

---

## 🛡️ リスク管理

### サーキットブレーカー

```python
circuit_breaker_rules = {
    "max_triggers_per_hour": 10,
    "max_positions_per_day": 5,
    "daily_loss_limit_usd": 20,
    "total_loss_limit_usd": 100,
}
```

### 損益管理

- **損切り:** -1%（固定ルール）
- **利確:** +1%到達時、AIが判断
- **最大保有時間:** 30分

---

## 📊 よく使うコマンド

```bash
# Phase 0
make phase0-notebook              # Jupyter起動

# Phase 1
make phase1-test-local            # ローカルテスト
make phase1-deploy-dev            # Dev環境デプロイ

# 共通
make aws-costs                    # AWS利用料確認
make lambda-logs                  # Lambdaログ確認
make help                         # 全コマンド一覧
```

---

## 📖 ドキュメント

- **[セットアップガイド](SETUP_GUIDE.md)** - 詳細な環境構築手順
- **[TDD セットアップガイド](docs/TDD_SETUP.md)** - SPEC駆動開発+TDD環境構築
- **[プロジェクトステータス](docs/PROJECT_STATUS.md)** - 現在の進捗状況
- [完全設計書（最終版）](docs/DESIGN_DOC_FINAL.md) - 4フェーズの詳細計画
- [Phase 0 README](phase0_data_analysis/README.md) - データ分析環境
- [Lambda README](lambda/README.md) - Lambda関数詳細
- [Terraform README](infrastructure/terraform/README.md) - インフラ設定

---

## 🎯 成功基準

### 技術的成功
- [ ] Phase 0-3を完走
- [ ] AIが統計的に有意なパターンを5つ以上発見
- [ ] AWS月額利用料が$30以内

### 学習的成功
- [ ] AIプロンプト設計スキルの習得
- [ ] 金融ニュース分析の体系的理解
- [ ] サーバーレス実装経験

### 財務的成功（副次的）
- [ ] 3ヶ月の損益が±$50以内
- [ ] 勝率50%以上

---

## ⚠️ 重要な注意事項

- **本プロジェクトは研究目的です。** 利益追求が主目的ではありません。
- **育児を最優先します。** システムは自律動作設計。週1回のメンテナンスのみ必須。
- **予算は消失可能な金額です。** 生活費には絶対に手をつけません。

---

## 📝 ライセンス

MIT License

---

## 🙏 謝辞

- **Gemini:** 設計レビューと技術的助言
- **Claude:** システム実装パートナー
- **家族:** 育児休暇中のプロジェクト遂行を支えてくれたことに感謝

---

**Last Updated:** 2025-11-16
**Current Phase:** ✅ フルセットアップ完了 → Phase 0開始可能

---

## 🎉 セットアップ完了！

全Phase（0-3）のテンプレート・スクリプト・インフラ設定が完了しました。

### 📊 作成されたもの

- **28個のディレクトリ**
- **30個以上のファイル**（Python, Terraform, Markdown, 設定ファイル等）

### 🚀 今すぐ始められます

```bash
# 詳細な手順は SETUP_GUIDE.md を参照
make setup
make install-deps
make phase0-setup
make phase0-download-data
make phase0-analyze
```

詳細は **[SETUP_GUIDE.md](SETUP_GUIDE.md)** と **[PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** を確認してください。
