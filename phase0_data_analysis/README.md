# Phase 0: Data Analysis & Pattern Discovery

**Goal:** AIに過去データから「黄金パターン（A案）」を発見させる

**期間:** Week 1-2

---

## 📋 Overview

Phase 0では、Kaggleの過去データを使用してAIに「ニュースの特徴 → 市場反応」の相関パターンを発見させます。

### 主要なステップ

1. **データ収集**: Kaggleからニュース+株価データセットをダウンロード
2. **特徴量エンジニアリング**: センチメント、キーワード、トピック等を抽出
3. **AI分析**: Claude/Geminiにパターン発見を依頼
4. **検証**: 発見したパターンの妥当性を評価

---

## 🚀 Quick Start

### 1. Setup

```bash
# Phase 0の環境をセットアップ
make phase0-setup

# .envファイルにAPIキーを設定
cp ../.env.example ../.env
# .envを編集: KAGGLE_USERNAME, KAGGLE_KEY, ANTHROPIC_API_KEY
```

### 2. Download Data

```bash
# Kaggleデータセットをダウンロード
make phase0-download-data
```

### 3. Analyze

```bash
# Option A: Jupyter Notebookで対話的に分析
make phase0-notebook

# Option B: スクリプトで自動実行
make phase0-analyze
```

### 4. Validate

```bash
# 発見したパターンを検証
make phase0-validate
```

---

## 📂 Directory Structure

```
phase0_data_analysis/
├── data/                  # Kaggleデータ（.gitignore済み）
│   ├── news.csv
│   └── stock_prices.csv
├── notebooks/             # Jupyter Notebook
│   └── 01_pattern_discovery.ipynb
├── outputs/               # 分析結果
│   ├── patterns_v1.json   # 発見したパターン（Phase 1で使用）
│   └── phase0_report.md   # 分析レポート
└── scripts/               # Python スクリプト
    ├── download_kaggle_data.py
    ├── feature_extraction.py
    ├── pattern_discovery.py
    └── validate_patterns.py
```

---

## 📊 Required Data

### Kaggle Dataset Keywords

以下のキーワードでKaggleを検索してデータセットを取得：

1. `"Financial News Headlines stock price"`
2. `"US stock earnings news sentiment"`
3. `"Daily News for Stock Market Prediction"`

### Data Schema

**ニュースデータ:**
- `date`: ニュース発表日時
- `headline`: 見出し
- `content`: 本文
- `symbol`: 対象銘柄（AAPL, MSFT等）

**株価データ:**
- `date`: 日付
- `symbol`: 銘柄コード
- `open`, `high`, `low`, `close`: OHLC
- `volume`: 出来高

---

## 🎯 Success Criteria

Phase 0完了の条件：

- [ ] Kaggleデータセット取得（過去1-2年分）
- [ ] 特徴量抽出スクリプト完成
- [ ] `patterns_v1.json` 生成（5-10個のパターン）
- [ ] `phase0_report.md` 作成（分析プロセスを文書化）
- [ ] 各パターンに統計的妥当性（サンプル数10件以上）

---

## 📖 Next Steps

Phase 0完了後、Phase 1へ移行：
- `patterns_v1.json` をAWS SSM Parameter Storeにアップロード
- リアルタイムシステムで発見したパターンを検証
