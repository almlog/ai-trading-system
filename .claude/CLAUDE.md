# Claude Code Project Rules

AI株式ニュース分析・自動取引システムの開発ルールとAIエージェント自律動作ガイド

---

## 🌳 Git Branch Strategy

### Branch Hierarchy

```
main (production)
  ↑
  └── release/* (staging)
        ↑
        └── develop (integration)
              ↑
              └── feature/* (development)
```

### Branch Rules

#### 1. **main** - Production Branch
- **目的**: 本番環境、安定版のみ
- **保護**: 直接コミット禁止
- **マージ元**: `release/*` ブランチのみ
- **タイミング**: Phase完了時のみ

#### 2. **release/*** - Release Branch
- **命名**: `release/phase0`, `release/phase1`, etc.
- **目的**: Phase完了前の最終テスト
- **マージ元**: `develop` ブランチ
- **マージ先**: `main` ブランチ（テスト完了後）
- **作業**: バグ修正のみ、新機能追加は禁止

#### 3. **develop** - Development Branch
- **目的**: 開発中の統合ブランチ
- **マージ元**: `feature/*` ブランチ
- **マージ先**: `release/*` ブランチ
- **日常作業**: 基本的にこのブランチで作業

#### 4. **feature/*** - Feature Branch
- **命名**: `feature/phase0-kaggle-download`, `feature/lambda-news-fetch`, etc.
- **目的**: 個別機能の開発
- **マージ元**: `develop` ブランチ
- **マージ先**: `develop` ブランチ
- **削除**: マージ後、速やかに削除

---

## 🔄 Development Workflow

### Daily Development

```bash
# 1. developブランチから作業開始
git checkout develop
git pull origin develop

# 2. フィーチャーブランチを作成
git checkout -b feature/your-feature-name

# 3. 開発作業
# ... コーディング、テスト ...

# 4. こまめにコミット
git add .
git commit -m "feat(scope): description"

# 5. developにマージ前にテスト
make test  # または適切なテストコマンド

# 6. developにマージ
git checkout develop
git merge feature/your-feature-name

# 7. プッシュ
git push origin develop

# 8. フィーチャーブランチ削除
git branch -d feature/your-feature-name
```

### Phase Completion

```bash
# 1. developからリリースブランチ作成
git checkout develop
git checkout -b release/phase0

# 2. 最終テスト・バグ修正
make phase0-validate
# バグがあれば修正してコミット

# 3. mainにマージ
git checkout main
git merge release/phase0

# 4. タグ付け
git tag -a v0.1.0 -m "Phase 0: Pattern Discovery Complete"

# 5. プッシュ
git push origin main
git push origin v0.1.0

# 6. リリースブランチ削除
git branch -d release/phase0
```

---

## 🧪 SPEC駆動開発 + TDD ワークフロー

### 開発の鉄則

**すべての機能開発は以下の順序で実行する（絶対厳守）：**

```
1. SPEC作成 → 2. TEST作成(RED) → 3. 実装(GREEN) → 4. REFACTOR → 5. DOC更新
```

### ステップ詳細

#### Step 1: SPEC作成（仕様定義）

**目的**: 何を作るか、どう動くべきかを明確に定義

**成果物**: `specs/` フォルダに仕様書を作成

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

#### Step 2: TEST作成（RED段階）

**目的**: 仕様に基づいたテストを先に書く

**ルール**:
- ❌ **実装コードより先にテストを書く（絶対厳守）**
- ✅ テストは失敗する（REDになる）ことを確認
- ✅ `tests/` フォルダに配置

```python
# tests/test_feature.py

import pytest
from module import FeatureClass

def test_feature_basic_functionality():
    """基本機能のテスト"""
    result = FeatureClass().do_something()
    assert result == expected_value

def test_feature_edge_case():
    """エッジケースのテスト"""
    with pytest.raises(ValueError):
        FeatureClass().do_something(invalid_input)
```

**実行**: `pytest tests/test_feature.py` → ❌ FAIL（実装前なので当然）

#### Step 3: 実装（GREEN段階）

**目的**: テストを通過させる最小限の実装

**ルール**:
- ✅ テストを通すための最小実装
- ❌ 過剰な実装はしない（YAGNI原則）
- ✅ すべてのテストがGREENになることを確認

```python
# module.py

class FeatureClass:
    def do_something(self, input_value=None):
        if input_value is None:
            return expected_value
        if not self._is_valid(input_value):
            raise ValueError("Invalid input")
        return self._process(input_value)
```

**実行**: `pytest tests/test_feature.py` → ✅ PASS

#### Step 4: REFACTOR（リファクタリング）

**目的**: コードの品質向上、可読性・保守性の改善

**必須チェック項目**:
- [ ] DRY原則: 重複コードの排除
- [ ] 関数の単一責任: 1つの関数は1つのことだけ
- [ ] 命名の明確性: 変数・関数名が意図を表現
- [ ] コメントの適切性: 複雑なロジックには説明を追加
- [ ] パフォーマンス: 不要な計算やループの削除
- [ ] エラーハンドリング: 適切な例外処理

**実行**: リファクタ後も `pytest tests/` → ✅ PASS（テストが壊れないこと）

#### Step 5: DOC更新（ドキュメント）

**目的**: 実装内容を記録し、他者（未来の自分）が理解できるようにする

**更新対象**:
- `README.md`: 新機能の追加を記載
- `docs/`: API仕様、使い方ガイド
- `CHANGELOG.md`: 変更履歴
- docstring: 関数・クラスのドキュメント

```python
def do_something(self, input_value=None):
    """
    入力値を処理して結果を返す

    Args:
        input_value (str, optional): 処理する値. Defaults to None.

    Returns:
        str: 処理結果

    Raises:
        ValueError: 入力値が無効な場合

    Examples:
        >>> obj = FeatureClass()
        >>> obj.do_something()
        'expected_value'
    """
```

---

### TDD 実行コマンド

```bash
# テスト実行
pytest tests/

# カバレッジ確認
pytest --cov=. tests/

# 特定のテストのみ
pytest tests/test_feature.py::test_specific_case

# 監視モード（ファイル変更時に自動実行）
pytest-watch
```

---

### 違反時の対応

**以下の行為は絶対禁止**:

❌ **テストを書かずに実装する**
→ 即座に実装を削除し、テストから書き直す

❌ **テストが失敗しているのに実装を進める**
→ GREENになるまで実装に集中

❌ **REFACTORを飛ばす**
→ リファクタリングを強制実行（品質保証のため）

❌ **ドキュメント更新を忘れる**
→ 機能追加のPRはドキュメント更新必須

---

### Phase別 TDD戦略

#### Phase 0: データ分析
- **SPEC**: `specs/phase0_pattern_discovery.md`
- **TEST**: Jupyter Notebookでの検証、assertion追加
- **重点**: データ処理ロジックの正確性

#### Phase 1: Lambda関数
- **SPEC**: `specs/lambda_*.md`
- **TEST**: `tests/lambda/test_*.py` + モックAWS（moto）
- **重点**: AWS連携、エラーハンドリング

#### Phase 2-3: 統合システム
- **SPEC**: `specs/integration_*.md`
- **TEST**: E2Eテスト、統合テスト
- **重点**: システム全体の動作保証

---

### MCP活用（推奨）

**Sequential Thinking MCP**:
- 複雑なロジックのステップバイステップ分析
- REFACTORの改善案提示

**Context7 MCP**:
- Pythonテストのベストプラクティス参照
- AWS Lambda テストパターン検索

---

## 🚫 Prohibited Actions

### mainブランチでの禁止事項

❌ **絶対に禁止**:
- 直接コミット
- 未テストのコードのマージ
- フィーチャーブランチから直接マージ

✅ **許可される操作**:
- `release/*` からのマージ（テスト完了後）
- タグ付け
- ドキュメント更新（緊急時のみ）

---

## 🎭 Persona Auto-Selection Rules

AIエージェント（Claude）が自律的にペルソナを選択するためのルール

### Decision Tree

```
ユーザーの質問・リクエストを受信
    │
    ├─ 技術実装・コード・デバッグ？
    │   └─→ @engineer を起動
    │
    ├─ スケジュール・優先度・リソース配分？
    │   └─→ @pm を起動
    │
    ├─ ビジョン・目的・価値判断・機能追加可否？
    │   └─→ @po を起動
    │
    └─ 学習記録・ブログ記事・振り返り？
        └─→ @blogger を起動
```

### Persona Selection Matrix

| Keywords in User Request | Selected Persona | Reason |
|--------------------------|------------------|--------|
| "実装", "コード", "バグ", "エラー", "Lambda", "DynamoDB", "API" | **@engineer** | 技術的な実装・問題解決 |
| "優先度", "スケジュール", "予算", "リスク", "Phase", "タスク" | **@pm** | プロジェクト管理・リソース配分 |
| "ビジョン", "目的", "価値", "ユーザー", "学習目標", "成功基準" | **@po** | 戦略・方向性・価値判断 |
| "ブログ", "Qiita", "記事", "devlog", "学び", "振り返り" | **@blogger** | 学習記録・技術発信 |

### Multi-Persona Situations

複数ペルソナの協議が必要な場合：

#### Case 1: 新機能追加リクエスト
```
User: "Phase 0で銘柄を10個に増やしたい"

Step 1: @po でビジョン判断
→ "Phase 0の目的は5銘柄でパターン発見。ビジョンに合致しない"

Step 2: @pm でリソース判断
→ "データ量2倍、分析時間2倍。スケジュールに影響"

Step 3: @engineer で技術的実現性
→ "実装は可能だが、Phase 0の範囲を超える"

Decision: ❌ Phase 0では対応しない。Phase 3完了後に検討
```

#### Case 2: 技術的問題発生
```
User: "Lambda関数がタイムアウトする"

Step 1: @engineer で技術調査
→ "Bedrockコールが30秒。timeout延長またはモデル最適化"

Step 2: @pm で影響評価
→ "Phase 1マイルストーンに影響なし。優先度Medium"

Decision: ✅ timeout延長で対応
```

#### Case 3: Phase移行判断
```
User: "Phase 0を完了してよい？"

Step 1: @engineer で技術評価
→ "patterns_v1.json生成済み、テストOK"

Step 2: @pm で完了基準確認
→ "パターン数7個（目標5個以上）、スケジュール通り"

Step 3: @po で価値評価
→ "学習目標達成、Phase 1に進む価値あり"

Decision: ✅ Phase 0完了、Phase 1へ移行
```

---

## 🤖 AI Agent Autonomous Behavior

### Automatic Persona Activation

AIエージェントは以下のルールで**自動的に**ペルソナを選択します：

#### 1. Keyword Detection
```python
def select_persona(user_input: str) -> str:
    # 技術キーワード
    if any(kw in user_input.lower() for kw in
           ['実装', 'コード', 'バグ', 'エラー', 'lambda', 'api', 'テスト']):
        return 'engineer'

    # PM キーワード
    if any(kw in user_input.lower() for kw in
           ['優先度', 'スケジュール', '予算', 'リスク', 'phase', 'タスク']):
        return 'pm'

    # PO キーワード
    if any(kw in user_input.lower() for kw in
           ['ビジョン', '目的', '価値', 'ユーザー', '学習', '成功']):
        return 'po'

    # Blogger キーワード
    if any(kw in user_input.lower() for kw in
           ['ブログ', 'qiita', '記事', 'devlog', '学び', '振り返り']):
        return 'blogger'

    # デフォルト（文脈による判断）
    return 'engineer'  # 技術プロジェクトのため
```

#### 2. Context Analysis

ユーザーの質問の文脈から判断：

- **"〇〇を実装したい"** → @engineer
- **"〇〇を追加すべきか？"** → @pm + @po
- **"Phase Xを完了してよい？"** → @engineer + @pm + @po
- **"今週の学びをまとめたい"** → @blogger

#### 3. Explicit Activation

ユーザーが明示的にペルソナを指定した場合：

```
User: "@engineer Lambda関数のタイムアウト設定は？"
→ engineerペルソナで回答

User: "@pm この機能の優先度は？"
→ pmペルソナで回答
```

---

## 📝 Commit Message Rules

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

### Scopes

- `phase0`: Phase 0関連
- `phase1`: Phase 1関連
- `lambda`: Lambda関数
- `terraform`: インフラ
- `docs`: ドキュメント

### Examples

```bash
git commit -m "feat(phase0): add Kaggle data download script"
git commit -m "fix(lambda): resolve DynamoDB timeout issue"
git commit -m "docs(readme): update setup guide with new steps"
git commit -m "refactor(phase1): optimize circuit breaker logic"
```

---

## 🔍 Code Review Checklist

### Before Merge to develop

- [ ] コードがlintを通過（`make lint`）
- [ ] テストが全て成功（`make test`）
- [ ] ドキュメント更新済み（必要に応じて）
- [ ] .envや秘密情報が含まれていない
- [ ] コミットメッセージが規約に従っている

### Before Merge to main (Phase完了時)

- [ ] Phase完了基準を全て満たしている
- [ ] 最終テスト・検証完了
- [ ] 成果物が生成されている（patterns_v1.json等）
- [ ] READMEの現在のPhaseステータス更新
- [ ] devlog記録済み
- [ ] タグ付け準備完了

---

## 🎯 Phase-Specific Rules

### Phase 0

- **Branch**: `feature/phase0-*` → `develop` → `release/phase0` → `main`
- **成果物**: `patterns_v1.json`, `phase0_report.md`
- **Tag**: `v0.1.0`

### Phase 1

- **Branch**: `feature/phase1-*` → `develop` → `release/phase1` → `main`
- **成果物**: 稼働中のAWSシステム、取引ログ
- **Tag**: `v1.0.0`

### Phase 2

- **Branch**: `feature/phase2-*` → `develop` → `release/phase2` → `main`
- **成果物**: `patterns_v2_raw.json`, 比較レポート
- **Tag**: `v2.0.0`

### Phase 3

- **Branch**: `feature/phase3-*` → `develop` → `release/phase3` → `main`
- **成果物**: 最終研究レポート、統合システム
- **Tag**: `v3.0.0`

---

## 🚀 Quick Commands

### Branch Operations

```bash
# developブランチに切り替え
git checkout develop

# 新しいフィーチャーブランチ作成
git checkout -b feature/your-feature-name

# developにマージ
git checkout develop
git merge feature/your-feature-name

# リリースブランチ作成
git checkout -b release/phase0

# mainにマージ（Phase完了時）
git checkout main
git merge release/phase0
git tag -a v0.1.0 -m "Phase 0 Complete"
git push origin main --tags
```

---

## 📚 Related Documents

- **[personas/README.md](../personas/README.md)** - ペルソナ詳細
- **[GITHUB_SETUP.md](../docs/GITHUB_SETUP.md)** - GitHub管理ガイド
- **[PROJECT_STATUS.md](../docs/PROJECT_STATUS.md)** - プロジェクト進捗

---

**このルールに従って、安全かつ効率的に開発を進めましょう！** 🚀
