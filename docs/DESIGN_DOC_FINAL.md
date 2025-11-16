# AIニュース分析・自動取引システム 設計書 最終版
## (予算5万円・米国株式版 / 4フェーズ構成)

---

## 📋 改訂履歴

### 主要な変更点と変更理由

| 項目 | 旧計画 | 最終計画 | 変更理由 |
|------|--------|----------|----------|
| **投資対象** | FX (USD/JPY) | **米国株式（テック大手5社）** | ニュース分析スキルが実務で活用しやすく、限られた時間で「自分の身になる」学びを優先 |
| **ニュースAPI** | OANDA本番口座での有料API（証拠金40,000円で利用権獲得） | **Finnhub/Alpha Vantage（無料枠）** | OANDAのリアルタイムニュースAPIは標準口座では利用不可と判明。無料APIでも十分な品質を確保可能 |
| **予算配分** | 証拠金40,000円 / インフラ10,000円 | **証拠金20,000円 / AWS 10,000円 / 予備費20,000円** | リスク分散。実現不可能な前提に予算の80%を投じるリスクを回避し、予備費を確保 |
| **Phase 0データ** | リアルタイムAPIで過去データ収集 | **Kaggle静的データセット** | APIの過去データ取得制限を回避。本質的な「パターン発見」に時間を集中投下 |
| **トリガー設計** | 10分間隔の定期ポーリング | **3パターンのイベント駆動型**（ニュース発生時/ボラティリティ監視/経済指標スケジュール） | 固定間隔は非効率。市場の動きに連動した合理的なトリガー設計 |
| **AI活用方針** | 人間が分析軸を定義 | **AIが黄金パターンを発見** | 研究目的を重視。AIの能力を最大限活用し、人間が想定しないパターンの発見を目指す |
| **フェーズ構成** | 未定義 | **4フェーズ（Phase 0-3）** | Phase 0-1で基本システム構築、Phase 2-3で生データ分析による精度向上を追求 |

---

## 1. プロジェクト概要

### 1.1 目的

育児休暇中の3ヶ月を活用し、AI（Claude/Gemini）による米国株式ニュース分析システムを構築する。

**本プロジェクトの主目的：**
1. AI研究（プロンプト設計と継続的改善）
2. ニュース分析スキルの習得
3. 金融市場の反応パターン分析手法の確立

**副次的目標：** AIサブスクリプション費用の回収（利益追求は二の次）

### 1.2 ゴール

**技術ゴール：**
- 米国企業ニュース・経済指標をトリガーに、AIが市場反応パターンを発見し、取引判断を通知・実行するシステムをAWSサーバーレス環境に構築

**学習ゴール：**
- AIプロンプト設計と継続的チューニングの実践スキル
- 金融ニュース分析の体系的理解
- AWS サーバーレスアーキテクチャの実装経験

**成果指標：**
- 3ヶ月でAIが発見した「統計的に有意なパターン」を3つ以上特定
- Phase 0-3を完走し、研究レポートを完成

### 1.3 主要制約

- **予算:** 50,000円（消失しても良い研究開発費）
- **期間:** 3ヶ月（Phase 0-3）
- **作業時間:** 育児と並行（システムは自律動作が前提）
- **技術スタック:** AWS (Lambda, S3, Bedrock, DynamoDB), Python, Finnhub/Alpha Vantage API

---

## 2. 予算配分（50,000円）

| 費目 | 金額 | 使途 |
|------|------|------|
| **証券口座 証拠金** | 20,000円 | 米国株式の小ロット取引用。AIの判断を実市場で検証する元手 |
| **AWS利用料** | 10,000円 | Lambda, Bedrock (Claude Haiku), S3, DynamoDB, EventBridge等の3ヶ月分従量課金 + バッファ |
| **予備費** | 20,000円 | Phase 0-3での実験費用、追加データ取得、予期せぬコスト対応 |
| **合計** | **50,000円** | |

**予算設計の哲学：**
- 証拠金を抑え（20,000円）、予備費を厚く確保（20,000円）することでリスク分散
- AWS費用は月額3,000円程度を想定（実績ベース）
- 無料APIを最大限活用し、有料サービスへの依存を最小化

---

## 3. 投資対象と戦略

### 3.1 対象市場

**米国株式市場（個別銘柄）**

### 3.2 対象銘柄

**テック大手5社:**
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Alphabet/Google)
- AMZN (Amazon)
- NVDA (NVIDIA)

**選定理由：**
1. ニュース量が豊富（AIの学習サンプルが多い）
2. 市場の注目度が高く、価格反応が明確
3. 5社の比較分析により、「銘柄固有」vs「市場共通」パターンを識別可能

### 3.3 研究戦略

**「AIによる黄金パターン発見」アプローチ**

#### Phase 0-1: A案（特徴量エンジニアリング）
1. 人間が設計した特徴量（センチメント、騰落率等）をAIに渡す
2. AIが「ニュースの特徴 → 市場反応」の相関パターンを発見
3. 発見したパターンをリアルタイムシステムで検証

#### Phase 2-3: B案（生データ分析）
1. Phase 0-1の結果をベースラインとして確立
2. AIに生データ（加工なし）を渡し、人間が想定しない特徴を発見させる
3. A案とB案の精度を比較し、優れた方（またはハイブリッド）を最終版とする

**人間の役割：**
- 週1回（日曜）：AIが発見したパターンの妥当性評価
- プロンプトの継続的改善
- 最終的な研究方向性の選択

---

## 4. システムアーキテクチャ

### 4.1 全体構成（3パターン統合型）

```
┌─────────────────────────────────────────────────────┐
│          3つの独立したトリガーシステム                │
└─────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
   [パターンA]      [パターンB]       [パターンC]
 ニュース発生時   ボラティリティ監視  経済指標スケジュール
         │                │                │
         └────────┬───────┴────────┬───────┘
                  ▼                        
           [EventBridge]          
          (Custom Events)         
                  │                  
                  ▼                        
          [サーキットブレーカー]
            (DynamoDB Check)
                  │
                  ▼
          [統合判断Lambda]
                  │
                  ▼
          [AI分析エンジン]
        (Bedrock Claude Haiku)
                  │
           ┌──────┴──────┐
           ▼              ▼
    [ポジション管理]   [SNS通知]
      (DynamoDB)      (Slack/LINE)
           │
           ▼
    [証券会社API]
    (取引実行)
```

### 4.2 パターン別トリガー設計

#### パターンA: ニュース発生時トリガー
```
EventBridge Scheduler (5分毎) 
  → Lambda (Finnhub News Fetch)
  → 新規ニュース検出（前回取得時刻と比較）
  → S3保存 + EventBridge Put Events
  → 統合判断Lambda起動
```

**実装詳細：**
- DynamoDB: `last_fetch_timestamp` で重複取得を防止
- 重要度フィルタ: Finnhubの `category` で決算/重要ニュースのみ抽出

#### パターンB: ボラティリティ監視型
```
EventBridge Scheduler (1分毎)
  → Lambda (Price Monitor)
  → Alpha Vantage APIで直近5分の価格取得
  → 変動率計算: abs((current - 5min_ago) / 5min_ago)
  → 閾値超過（±2%）検出
  → EventBridge Put Events
  → 統合判断Lambda起動
```

**閾値設定：**
- AAPL, MSFT, GOOGL: ±2%
- AMZN, NVDA: ±2.5%（ボラティリティが高いため）

#### パターンC: 経済指標スケジュール型
```
DynamoDB Table: economic_calendar
  ← 事前登録: FOMC, 雇用統計, CPI等の日時

EventBridge Scheduler (15分毎)
  → Lambda (Calendar Checker)
  → 現在時刻が「発表30分前」または「発表直後」かチェック
  → EventBridge Put Events
  → 統合判断Lambda起動
```

**登録イベント例：**
```json
{
  "event_name": "FOMC Meeting Decision",
  "scheduled_time": "2025-03-20T14:00:00-04:00",
  "impact_level": "High"
}
```

### 4.3 サーキットブレーカー（異常動作防止）

**DynamoDBテーブル: `trigger_history`**

```python
circuit_breaker_rules = {
    "max_triggers_per_hour": 10,        # 1時間に最大10回
    "max_positions_per_day": 5,         # 1日の取引回数上限
    "min_interval_seconds": 300,        # 最低5分間隔
    "daily_loss_limit_usd": 20,         # 1日の損失上限 $20
    "total_loss_limit_usd": 100,        # プロジェクト全体の損失上限 $100
}
```

**動作フロー：**
```python
def check_circuit_breaker(trigger_type):
    # 1. 過去1時間のトリガー回数をチェック
    recent_count = query_dynamodb(last_hour=True)
    if recent_count >= 10:
        log_and_notify("⚠️ 1時間のトリガー上限到達")
        return False
    
    # 2. 本日の損益をチェック
    daily_pnl = calculate_today_pnl()
    if daily_pnl <= -20:
        log_and_notify("🚨 本日の損失上限到達。明日まで全停止")
        return False
    
    # 3. 累積損失をチェック
    total_pnl = calculate_total_pnl()
    if total_pnl <= -100:
        log_and_notify("🚨🚨 プロジェクト損失上限到達。システム完全停止")
        disable_all_triggers()
        return False
    
    return True
```

---

## 5. 4フェーズ実装ロードマップ

### Phase 0: 基礎構築とパターン発見（Week 1-2）

**ゴール:** AIに過去データから「黄金パターン（A案）」を発見させる

#### 5.1 データ収集

**Kaggleデータセット検索キーワード：**
1. `"Financial News Headlines stock price"`
2. `"US stock earnings news sentiment"`
3. `"Daily News for Stock Market Prediction"`

**必要なデータ項目：**
- ニュース: 日時、見出し、本文、対象銘柄
- 株価: 日時、OHLC（始値・高値・安値・終値）、出来高

**期間:** 過去1-2年分

#### 5.2 特徴量エンジニアリング（A案）

**ニュース側特徴量：**
```python
features_news = {
    "sentiment_score": float,  # -1.0 (ネガティブ) 〜 +1.0 (ポジティブ)
    "keywords": list,          # ["beat", "expectations", "downgrade"]
    "topic": str,              # "Earnings" / "M&A" / "Legal" / "Product"
    "announcement_time": str,  # "market_hours" / "pre_market" / "after_market"
}
```

**株価側特徴量：**
```python
features_stock = {
    "pre_announcement_trend": float,    # 発表前5日間の騰落率 (%)
    "volatility_5d": float,             # 過去5日間の標準偏差
    "volume_spike": float,              # 出来高の前日比倍率
}
```

**特徴量抽出ツール:**
- センチメント分析: `VADER` または `TextBlob`
- キーワード抽出: `TF-IDF` または Claude API
- トピック分類: Claude APIにプロンプトで依頼

#### 5.3 AI分析プロンプト（Phase 0専用）

```
あなたは金融データサイエンティストです。

【データ】
以下は過去1年分の「ニュースの特徴量」と「その後の株価変動」のペアです。
[CSVデータまたはJSON配列]

【あなたのタスク】
「どのような特徴のニュース」が「どのような市場状況」で発表されると、
「株価がどう動くか」の相関パターンを発見してください。

【求める出力】
以下のJSON形式で、5-10個のパターンを報告してください。

{
  "patterns": [
    {
      "pattern_id": "earnings_beat_selloff",
      "name": "好決算後の利益確定売り",
      "conditions": [
        "sentiment_score > 0.5",
        "pre_announcement_trend > 5.0",
        "topic == 'Earnings'"
      ],
      "prediction": {
        "direction": "Down",
        "magnitude": "-2% within 1 hour",
        "confidence": 0.72
      },
      "sample_size": 23,
      "hypothesis": "材料出尽くし。短期筋の利益確定"
    }
  ]
}

【制約】
- 統計的に有意なパターンのみ（最低10件以上の事例）
- 各パターンには「なぜそうなるか」の仮説を必ず付ける
```

**実行環境:** ローカルまたは AWS Bedrock

#### 5.4 Phase 0 成果物

- `patterns_v1.json`: AIが発見した黄金パターンのリスト
- `phase0_analysis_report.md`: 分析プロセスと発見事項のサマリー
- `feature_extraction_pipeline.py`: Phase 1で再利用する特徴量抽出コード

**所要時間:** 1-2週間

---

### Phase 1: リアルタイムシステム構築と実運用（Week 3 - Month 2）

**ゴール:** Phase 0で発見したパターンを使い、自動取引システムを稼働させる

#### 5.5 AWSインフラ構築

**必要なリソース:**
```bash
# IAMロール
- lambda-execution-role (Lambda, S3, Bedrock, DynamoDB, SNS へのアクセス)

# S3バケット
- news-archive-bucket (ニュース生データ)
- pattern-library-bucket (patterns_v1.json格納)

# DynamoDB テーブル
- trigger_history (トリガー履歴とサーキットブレーカー)
- positions (現在のポジション管理)
- economic_calendar (経済指標スケジュール)

# Lambda関数
- news_fetch_lambda
- price_monitor_lambda
- calendar_checker_lambda
- unified_judgment_lambda
- ai_analysis_lambda
- position_manager_lambda

# EventBridge Rules
- news-fetch-schedule (rate: 5 minutes)
- price-monitor-schedule (rate: 1 minute)
- calendar-check-schedule (rate: 15 minutes)

# SNS トピック
- trading-alerts (Slack/LINE通知用)

# SSM Parameter Store
- /ai-trading/patterns (Phase 0の結果)
- /ai-trading/prompts/realtime-analysis
- /ai-trading/prompts/exit-evaluation
```

**実装方法:** Claude-code または AWS CLI + Terraform

#### 5.6 リアルタイム分析プロンプト

**SSM: `/ai-trading/prompts/realtime-analysis`**

```
あなたは以下の「黄金パターン」を学習済みです：
{patterns_from_phase0}

【新規ニュース】
見出し: {headline}
本文: {content}
対象銘柄: {symbol}
発表時刻: {timestamp}

【現在の市場状況】
- 現在価格: ${current_price}
- 発表前5日間の騰落率: {pre_trend}%
- 直近の出来高: {volume} (前日比 {volume_ratio}x)

【あなたのタスク】
1. このニュースが「黄金パターン」のどれに最もマッチするか判定
2. マッチ度（0-100）を算出
3. 推奨アクション（Buy/Sell/Hold）を決定

【出力形式】
以下のJSON形式で出力してください。
{
  "matched_pattern_id": "earnings_beat_selloff",
  "match_score": 85,
  "action": "Sell",
  "confidence": "High",
  "reasoning": "センチメントは+0.8とポジティブだが、発表前5日で+7%上昇済み。
               パターン'earnings_beat_selloff'に該当。材料出尽くしの可能性が高い。",
  "entry_price": 180.50,
  "target_profit": 1.0,
  "stop_loss": -1.0
}
```

#### 5.7 エントリー条件

```python
def should_enter_position(ai_analysis):
    return (
        ai_analysis["confidence"] == "High" and
        ai_analysis["match_score"] >= 80 and
        circuit_breaker_ok() and
        no_existing_position_for_symbol()
    )
```

#### 5.8 エグジット戦略

**損切り:** 固定ルール
```python
stop_loss = -1.0  # -1%で自動損切り
```

**利確:** AIによる判断型

**トリガー条件:** 含み益 +1% 到達時

**SSM: `/ai-trading/prompts/exit-evaluation`**

```
あなたは{minutes_ago}分前に以下の理由で{action}を推奨しました：
パターン: {matched_pattern}
理由: {original_reasoning}

【現在の状況】
- エントリー価格: ${entry_price}
- 現在価格: ${current_price}
- 含み損益: {pnl}% (${pnl_usd})
- エントリー後の最高値: ${peak_price}

【市場の動き】
- 直近5分の変動: {recent_trend}
- 出来高の変化: {volume_change}

【あなたのタスク】
このポジションを「保持」すべきか「決済」すべきか判断してください。

【出力形式】
{
  "decision": "Hold" or "Exit",
  "reasoning": "...",
  "confidence": "High" / "Medium" / "Low"
}
```

**再評価タイミング:**
- 含み益+1%到達時（初回）
- その後、5分ごと
- 最大保有時間: 30分（強制決済）

#### 5.9 Phase 1 成果物

- 稼働中のAWS自動取引システム
- 1ヶ月分の取引ログ（DynamoDB）
- 週次レビューレポート（AIの的中率、プロンプト改善履歴）

**所要時間:** 3-5週間

---

### Phase 2: 生データ分析への挑戦（Month 2後半 - Month 3前半）

**ゴール:** B案（生データ）でAIに新たなパターンを発見させ、A案と比較する

#### 5.10 Phase 2の位置づけ

Phase 1のシステムは**稼働させ続けながら**、並行して以下を実施：

1. Phase 0と同じKaggleデータセットを使用
2. 今度は**特徴量を作らず**、生のニューステキストと株価をAIに渡す
3. AIが「人間が想定しない特徴」を発見できるか実験

#### 5.11 B案プロンプト（Phase 2専用）

```
あなたは金融データサイエンティストです。

【データ】
以下は過去1年分の「ニュース記事（生テキスト）」と「その後の株価変動」です。
[JSON配列: {news_text, symbol, timestamp, price_before, price_after_1h, ...}]

【重要な指示】
私（人間）は、あなたに「特徴量」を与えていません。
あなた自身が、生のテキストと数値から「隠れたパターン」を発見してください。

例えば：
- 「特定の言い回し」（例："guidance was raised" vs "raised guidance"）
- 「文章の長さ」や「数字の出現頻度」
- 「発表時刻」や「曜日」との相関
- その他、人間が気づかない特徴

【求める出力】
以下のJSON形式で、発見したパターンを報告してください。

{
  "patterns": [
    {
      "pattern_id": "...",
      "discovered_feature": "ニュースの最初の段落に'however'が含まれる",
      "correlation": "この特徴がある場合、67%の確率で1時間後に-1.5%下落",
      "sample_size": 15,
      "hypothesis": "最初に好材料を述べ、'however'で反転する記事は
                     市場がネガティブと解釈しやすい"
    }
  ]
}
```

#### 5.12 A案 vs B案の比較評価

**比較指標:**
1. **パターン数:** A案とB案で、いくつのパターンを発見したか
2. **的中率:** 過去データでバックテスト（発見したパターンが実際に当たるか）
3. **新規性:** B案が「A案では発見できなかったパターン」を見つけたか

**評価シート例:**
```
| 項目 | A案（特徴量） | B案（生データ） |
|------|--------------|----------------|
| 発見パターン数 | 8個 | 12個 |
| 的中率（平均） | 68% | 71% |
| 新規パターン | - | 「文末が疑問文の決算発表は下落しやすい」等 3個 |
```

#### 5.13 Phase 2 成果物

- `patterns_v2_raw.json`: B案で発見したパターン
- `ab_comparison_report.md`: A案とB案の詳細比較レポート

**所要時間:** 2週間

---

### Phase 3: 最終統合と研究成果まとめ（Month 3後半）

**ゴール:** Phase 2の結果をシステムに反映し、3ヶ月の研究を総括する

#### 5.14 Phase 2結果のシステム統合

**ケース1: B案が優秀だった場合**
```bash
# SSM Parameter Storeを更新
aws ssm put-parameter \
  --name /ai-trading/patterns \
  --value file://patterns_v2_raw.json \
  --overwrite

# プロンプトも生データ用に更新
aws ssm put-parameter \
  --name /ai-trading/prompts/realtime-analysis \
  --value file://prompt_v2_raw.txt \
  --overwrite
```

**ケース2: A案が依然優秀な場合**
- Phase 1のシステムをそのまま継続

**ケース3: ハイブリッドが最適な場合**
```python
# 統合判断Lambdaで両方のプロンプトを実行
result_a = invoke_bedrock(patterns_v1, prompt_a)
result_b = invoke_bedrock(patterns_v2, prompt_b)

# 両方の結果を比較し、confidence が高い方を採用
final_decision = max([result_a, result_b], key=lambda x: x["confidence"])
```

#### 5.15 自動評価システム構築

**Lambda: `daily_performance_evaluator`**

```python
def evaluate_daily_performance():
    """
    毎日、AIの予測精度を自動計算
    """
    trades_today = query_dynamodb_positions(date=today)
    
    results = {
        "total_trades": len(trades_today),
        "winning_trades": 0,
        "losing_trades": 0,
        "total_pnl": 0.0,
        "accuracy": 0.0
    }
    
    for trade in trades_today:
        if trade["pnl"] > 0:
            results["winning_trades"] += 1
        else:
            results["losing_trades"] += 1
        results["total_pnl"] += trade["pnl"]
    
    results["accuracy"] = results["winning_trades"] / results["total_trades"]
    
    # S3にCSV追記
    append_to_s3("performance_log.csv", results)
    
    return results
```

**EventBridge:** 毎日23:59に実行

#### 5.16 最終研究レポート作成

**レポート構成:**

```markdown
# AIニュース分析・自動取引システム 研究レポート

## 1. エグゼクティブサマリー
- 3ヶ月の成果（パターン発見数、的中率、損益）
- 主要な学び

## 2. Phase 0: パターン発見
- 使用データセット
- 特徴量設計（A案）
- 発見したパターン8個の詳細

## 3. Phase 1: システム構築と実運用
- アーキテクチャ図
- 実際の取引例3件（成功/失敗）
- プロンプト改善の履歴

## 4. Phase 2: 生データ分析（B案）
- A案との比較結果
- B案で新たに発見したパターン
- 「AIが人間を超えた」事例

## 5. Phase 3: 統合と評価
- 最終的に採用したアプローチ
- 3ヶ月の累積成績
  - 総取引回数
  - 勝率
  - 総損益
  - 最大ドローダウン

## 6. 失敗事例と学び
- うまくいかなかったパターン
- システムのバグと対策
- AIプロンプト設計の試行錯誤

## 7. 今後の展望
- 3ヶ月後も継続する場合の改善案
- 学んだスキルの他分野への応用
```

#### 5.17 Phase 3 成果物

- `final_research_report.md`: 最終研究レポート（20-30ページ）
- `patterns_final.json`: 最終版の黄金パターンライブラリ
- `performance_dashboard.html`: 3ヶ月の成績を可視化したダッシュボード

**所要時間:** 2週間

---

## 6. リスク管理

### 6.1 財務リスク

```python
risk_parameters = {
    # 1日あたりの制限
    "max_daily_loss_usd": 20,
    "max_daily_trades": 5,
    
    # 1取引あたりの制限
    "max_position_size": 1,      # 株数
    "max_holding_time_sec": 1800,  # 30分
    
    # 取引ごとの損益管理
    "stop_loss_pct": -1.0,       # -1%で自動損切り
    "take_profit_trigger_pct": 1.0,  # +1%でAI判断開始
    
    # プロジェクト全体
    "total_budget_usd": 200,
    "emergency_stop_loss_pct": 0.7,  # 総資産が70%を下回ったら全停止
}
```

### 6.2 技術リスク

| リスク | 対策 |
|--------|------|
| **API制限超過** | Finnhub無料枠: 60 calls/分。Lambda側で`time.sleep()`でレート制限 |
| **Lambda タイムアウト** | 長時間処理（Phase 0のデータ分析）はローカルまたはSageMaker |
| **Bedrock利用料超過** | CloudWatch Alarm: 月額$50超過時に通知 + 自動停止 |
| **証券口座API障害** | エラー時は通知のみ送信し、手動取引に切り替え |
| **DynamoDB書き込みエラー** | Lambda内でリトライ（exponential backoff） |

### 6.3 運用リスク

**育児優先の原則:**
- システムは完全自律動作（24/7稼働）
- 通知への即座の反応は不要
- 週1回（日曜30分）のメンテナンスのみ必須

**緊急停止手順:**
```bash
# 全トリガーを無効化
aws events disable-rule --name news-fetch-schedule
aws events disable-rule --name price-monitor-schedule
aws events disable-rule --name calendar-check-schedule

# ポジション強制決済（手動）
# 証券会社のWebサイトまたはアプリで全ポジションをクローズ
```

---

## 7. 成功基準

### 7.1 技術的成功

- [ ] Phase 0-3 を完走
- [ ] 3パターンのトリガーが3ヶ月間、安定稼働
- [ ] AIが「統計的に有意なパターン」を5つ以上発見
- [ ] AWS月額利用料が$30以内に収まる

### 7.2 学習的成功

- [ ] AIプロンプト設計の実践スキルを習得（10回以上の改善サイクル）
- [ ] 金融ニュース分析の体系的理解（最終レポートで証明）
- [ ] サーバーレスアーキテクチャの実装経験（GitHub公開可能なレベル）

### 7.3 財務的成功（副次的）

- [ ] 3ヶ月の損益が ±$50以内（大損せず、研究費回収の目処）
- [ ] 勝率 50%以上
- [ ] 最大ドローダウン $30以内

---

## 8. 各Phase の期間と開始条件

| Phase | 期間 | 開始条件 | 成果物 |
|-------|------|----------|--------|
| **Phase 0** | Week 1-2 | プロジェクト開始 | `patterns_v1.json`（A案） |
| **Phase 1** | Week 3 - Month 2 | Phase 0完了 | 稼働システム + 取引ログ |
| **Phase 2** | Month 2後半 - Month 3前半 | Phase 1が安定稼働 | `patterns_v2_raw.json`（B案） + 比較レポート |
| **Phase 3** | Month 3後半 | Phase 2完了 | 最終研究レポート + 統合システム |

---

## 9. まとめ

本計画書は、以下の3つの柱に基づいて設計されています：

1. **実現可能性:** 無料APIとKaggleデータを活用し、技術的・予算的リスクを最小化
2. **学習の深さ:** 4フェーズで段階的に難易度を上げ、A案→B案で「AIの可能性」を追求
3. **育児との両立:** 自律動作システムにより、週1回のメンテナンスのみで継続可能

この計画により、3ヶ月という限られた期間で「AI研究」「実装スキル」「金融分析」の3つを同時に習得し、研究レポートとして形に残すことができます。

---