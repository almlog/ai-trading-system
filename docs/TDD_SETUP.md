# TDD & SPEC駆動開発 セットアップガイド

**最終更新**: 2025-11-17

---

## 📋 概要

このプロジェクトでは、**SPEC駆動開発 + TDD（Test-Driven Development）** をデフォルトの開発手法として採用しています。

**開発の流れ**:
```
1. SPEC作成 → 2. TEST作成(RED) → 3. 実装(GREEN) → 4. REFACTOR → 5. DOC更新
```

---

## 🛠️ セットアップ

### 1. Python依存パッケージのインストール

```bash
# pytest とカバレッジツールのインストール
pip install pytest pytest-cov pytest-watch

# AWS Lambda用のモックライブラリ（Phase 1以降）
pip install moto boto3

# requirements.txtに追加
echo "pytest>=7.4.0" >> requirements.txt
echo "pytest-cov>=4.1.0" >> requirements.txt
echo "pytest-watch>=4.2.0" >> requirements.txt
echo "moto>=4.2.0" >> requirements.txt
```

### 2. MCP サーバーのインストール（推奨）

SPEC駆動開発とTDDをより効率的に進めるため、以下のMCPサーバーをインストールすることを推奨します。

#### Sequential Thinking MCP

複雑なロジックのステップバイステップ分析、リファクタリング改善案の提示に使用します。

```bash
# グローバルインストール
npm install -g @modelcontextprotocol/server-sequential-thinking

# または、プロジェクトごとにnpx経由で自動実行（.claude/settings.json設定済み）
```

#### Context7 MCP

Pythonテストのベストプラクティス、AWS Lambdaテストパターンの参照に使用します。

```bash
# グローバルインストール
npm install -g @context7/mcp-server

# または、npx経由で自動実行（.claude/settings.json設定済み）
```

**確認方法**:

```bash
# Sequential Thinking が使えるか確認
npx -y @modelcontextprotocol/server-sequential-thinking --version

# Context7 が使えるか確認
npx -y @context7/mcp-server --version
```

### 3. Claude Code 設定の確認

`.claude/settings.json` に以下の設定が含まれていることを確認してください：

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"]
    }
  },
  "rules": [
    "すべての機能開発は SPEC → TEST(RED) → 実装(GREEN) → REFACTOR → DOC の順序で実行",
    "テストを書かずに実装コードを書くことは禁止",
    "REFACTORステップは必須（スキップ禁止）",
    "すべてのテストがPASSすることを確認してからコミット"
  ],
  "defaultWorkflow": "spec-driven-tdd",
  "testFramework": "pytest"
}
```

---

## 🚀 使い方

### スラッシュコマンド

Claude Codeで以下のスラッシュコマンドが使えます：

#### `/tdd`
TDDワークフロー全体を開始します。SPEC作成から始まり、TEST→実装→REFACTOR→DOCまで順番にガイドします。

```
/tdd
```

#### `/spec`
SPEC（仕様書）を作成します。機能の要件、入力・出力、成功基準を定義します。

```
/spec
```

#### `/test`
テストを作成・実行します（RED段階）。

```
/test
```

#### `/refactor`
リファクタリングを実行します（REFACTOR段階）。6つのチェック項目をガイドします。

```
/refactor
```

---

## 📂 ディレクトリ構成

```
ai-trading-system/
├── specs/                    # SPEC（仕様書）
│   ├── phase0_*.md
│   ├── lambda_*.md
│   └── ...
├── tests/                    # テストコード
│   ├── test_*.py
│   ├── lambda/
│   │   └── test_*.py
│   └── ...
├── .claude/
│   ├── CLAUDE.md            # TDDワークフロー定義
│   ├── settings.json        # MCP設定、ルール
│   └── commands/            # スラッシュコマンド
│       ├── tdd.md
│       ├── spec.md
│       ├── test.md
│       └── refactor.md
└── ...
```

---

## 📝 ワークフロー詳細

### Step 1: SPEC作成

```bash
/spec
```

機能の仕様を `specs/[機能名].md` に定義します。

**テンプレート**:
```markdown
# specs/feature_name.md

## 概要
何を実装するか

## 要件
- 機能要件1
- 機能要件2

## 入力・出力
- Input: ...
- Output: ...

## 制約条件
- ...

## 成功基準
- テストケース1
- テストケース2
```

### Step 2: TEST作成（RED）

```bash
/test
```

SPECに基づいてテストを先に書きます。`tests/test_*.py` に配置。

**実行**:
```bash
pytest tests/test_feature.py
```

**期待結果**: ❌ FAIL（実装前なので当然）

### Step 3: 実装（GREEN）

テストを通過させる最小限の実装を行います。

**実行**:
```bash
pytest tests/test_feature.py
```

**期待結果**: ✅ PASS

### Step 4: REFACTOR

```bash
/refactor
```

コードの品質を向上させます。6つのチェック項目：
1. DRY原則
2. 単一責任
3. 命名の明確性
4. コメントの適切性
5. パフォーマンス
6. エラーハンドリング

**実行**:
```bash
pytest tests/  # リファクタ後もPASSすること
```

### Step 5: DOC更新

ドキュメントを更新します：
- README.md
- docs/
- docstring
- CHANGELOG.md

---

## 🎯 Phase別 TDD戦略

### Phase 0: データ分析
- **SPEC**: `specs/phase0_pattern_discovery.md`
- **TEST**: Jupyter Notebookでの検証、assertion追加
- **重点**: データ処理ロジックの正確性

### Phase 1: Lambda関数
- **SPEC**: `specs/lambda_*.md`
- **TEST**: `tests/lambda/test_*.py` + モックAWS（moto）
- **重点**: AWS連携、エラーハンドリング

**Lambda テスト例**:
```python
import boto3
from moto import mock_dynamodb
import pytest

@mock_dynamodb
def test_circuit_breaker():
    # DynamoDBモックを作成
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='circuit_breaker',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}]
    )

    # テスト実行
    from lambda.utils.circuit_breaker import check_circuit_breaker
    result = check_circuit_breaker('news_trigger')

    assert result['allowed'] == True
```

### Phase 2-3: 統合システム
- **SPEC**: `specs/integration_*.md`
- **TEST**: E2Eテスト、統合テスト
- **重点**: システム全体の動作保証

---

## 🔍 テストコマンド集

```bash
# すべてのテスト実行
pytest tests/

# 特定のテストファイル
pytest tests/test_feature.py

# 特定のテストケース
pytest tests/test_feature.py::test_specific_case

# カバレッジ付き
pytest --cov=. tests/

# カバレッジレポート（HTML）
pytest --cov=. --cov-report=html tests/
open htmlcov/index.html

# 詳細出力
pytest -v tests/

# 失敗したテストのみ再実行
pytest --lf tests/

# 監視モード（ファイル変更時に自動実行）
pytest-watch
```

---

## ⚠️ 禁止事項

以下の行為は**絶対禁止**です：

❌ **テストを書かずに実装する**
→ 即座に実装を削除し、テストから書き直す

❌ **テストが失敗しているのに実装を進める**
→ GREENになるまで実装に集中

❌ **REFACTORを飛ばす**
→ リファクタリングを強制実行（品質保証のため）

❌ **ドキュメント更新を忘れる**
→ 機能追加のPRはドキュメント更新必須

---

## 🎓 参考リソース

- **プロジェクトルール**: `.claude/CLAUDE.md`
- **スラッシュコマンド**: `.claude/commands/`
- **pytest ドキュメント**: https://docs.pytest.org/
- **moto（AWS Mock）**: https://docs.getmoto.org/

---

## 📞 トラブルシューティング

### MCPサーバーが動かない

```bash
# Node.jsのバージョン確認（18以上推奨）
node --version

# npxで直接実行してみる
npx -y @modelcontextprotocol/server-sequential-thinking
```

### テストが見つからない

```bash
# pytestがtests/を見つけられるか確認
pytest --collect-only

# PYTHONPATHを設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

---

**Let's start TDD!** 🧪🚀
