# TDD クイックスタート

**問題**: `/tdd` などのスラッシュコマンドが認識されない場合の対処法

---

## 📌 スラッシュコマンドのトラブルシューティング

### 問題: "Unknown slash command: tdd"

**原因**: Claude Codeセッションがコマンドファイルを読み込んでいない

**解決策**:

1. **Claude Codeを再起動**
   - VSCode/エディタを再起動
   - または Claude Code セッションを終了して再開

2. **ファイルの確認**
   ```bash
   ls .claude/commands/
   # tdd.md, spec.md, test.md, refactor.md があることを確認
   ```

3. **代替方法**: `.claude/CLAUDE.md` を直接参照

---

## 🚀 TDDワークフロー（代替方法）

スラッシュコマンドが使えない場合、以下の手順で進めてください。

### Step 1: SPEC作成

**質問**:
1. どの機能を実装しますか？
2. 入力と出力は何ですか？
3. 制約条件や成功基準は何ですか？

**実行**:
```bash
# specs/ディレクトリに仕様書を作成
# 例: specs/kaggle_download.md
```

**テンプレート**:
```markdown
# specs/[機能名].md

## 概要
何を実装するか（1-2文）

## 要件
- 機能要件1
- 機能要件2

## 入力・出力
- Input: ...
- Output: ...

## 制約条件
- ...

## 成功基準
- [ ] テストケース1
- [ ] テストケース2
```

---

### Step 2: TEST作成（RED）

**実行**:
```bash
# tests/ディレクトリにテストファイルを作成
# 例: tests/test_kaggle_download.py
```

**テンプレート**:
```python
import pytest
from module import FeatureClass

def test_basic_functionality():
    """基本機能のテスト"""
    result = FeatureClass().do_something()
    assert result == expected_value

def test_edge_case():
    """エッジケースのテスト"""
    with pytest.raises(ValueError):
        FeatureClass().do_something(invalid_input)
```

**実行して失敗を確認（RED）**:
```bash
pytest tests/test_*.py
# ❌ FAIL（実装前なので当然）
```

---

### Step 3: 実装（GREEN）

**実行**:
テストを通過させる最小限の実装を行う

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

**テストが成功することを確認（GREEN）**:
```bash
pytest tests/test_*.py
# ✅ PASS
```

---

### Step 4: REFACTOR

**チェックリスト**:
- [ ] **DRY原則**: 重複コードの排除
- [ ] **単一責任**: 1つの関数は1つのことだけ
- [ ] **命名の明確性**: 変数・関数名が意図を表現
- [ ] **コメントの適切性**: 複雑なロジックに説明を追加
- [ ] **パフォーマンス**: 不要な計算やループの削除
- [ ] **エラーハンドリング**: 適切な例外処理

**リファクタ後もテストがPASS**:
```bash
pytest tests/
# ✅ PASS（テストが壊れていないこと）
```

---

### Step 5: DOC更新

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

## 🧪 テストコマンド集

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

# 詳細出力
pytest -v tests/

# 失敗したテストのみ再実行
pytest --lf tests/

# 監視モード（ファイル変更時に自動実行）
pytest-watch
```

---

## 📋 Phase 0 でTDDを始める例

### 実装例: Kaggleデータダウンロード機能

#### 1. SPEC作成

`specs/kaggle_download.md`:
```markdown
## 概要
Kaggle APIを使って米国株式ニュースデータセットをダウンロードする

## 要件
- Kaggle APIキーの認証
- データセットの検索
- データセットのダウンロード
- ダウンロード先の指定

## 入力・出力
- Input: dataset_name (str), output_dir (str)
- Output: ダウンロードしたファイルのパスリスト

## 制約条件
- Kaggle APIキーが設定されていること
- ネットワーク接続が必要

## 成功基準
- [ ] 指定したデータセットがダウンロードされる
- [ ] ダウンロード先に.csvファイルが存在する
- [ ] エラー時に適切な例外が発生する
```

#### 2. TEST作成

`tests/test_kaggle_download.py`:
```python
import pytest
from pathlib import Path
from scripts.download_kaggle_data import KaggleDownloader

def test_download_dataset():
    """基本的なダウンロード機能のテスト"""
    downloader = KaggleDownloader()
    files = downloader.download('dataset/name', './data')

    assert len(files) > 0
    assert all(Path(f).exists() for f in files)

def test_invalid_dataset_name():
    """無効なデータセット名のテスト"""
    downloader = KaggleDownloader()

    with pytest.raises(ValueError):
        downloader.download('', './data')
```

#### 3. 実装

`scripts/download_kaggle_data.py`:
```python
from kaggle.api.kaggle_api_extended import KaggleApi
from pathlib import Path

class KaggleDownloader:
    def __init__(self):
        self.api = KaggleApi()
        self.api.authenticate()

    def download(self, dataset_name, output_dir):
        if not dataset_name:
            raise ValueError("Dataset name is required")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.api.dataset_download_files(dataset_name, path=output_dir, unzip=True)

        return list(output_path.glob('*.csv'))
```

#### 4. REFACTOR

リファクタリング例:
```python
class KaggleDownloader:
    def __init__(self):
        self.api = self._authenticate()

    def _authenticate(self):
        """Kaggle API認証（単一責任）"""
        api = KaggleApi()
        api.authenticate()
        return api

    def _validate_dataset_name(self, dataset_name):
        """データセット名のバリデーション（分離）"""
        if not dataset_name:
            raise ValueError("Dataset name is required")

    def download(self, dataset_name, output_dir):
        """データセットのダウンロード"""
        self._validate_dataset_name(dataset_name)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.api.dataset_download_files(
            dataset_name,
            path=str(output_path),
            unzip=True
        )

        return self._get_downloaded_files(output_path)

    def _get_downloaded_files(self, output_path):
        """ダウンロードされたファイルの取得（分離）"""
        return list(output_path.glob('*.csv'))
```

#### 5. DOC更新

- `README.md` に使用例を追加
- `phase0_data_analysis/README.md` に手順を記載
- docstringを追加

---

## ⚠️ 重要なルール

**以下は絶対禁止**:

❌ テストを書かずに実装する
❌ テストが失敗しているのに実装を進める
❌ REFACTORを飛ばす
❌ ドキュメント更新を忘れる

**必ず守る**:

✅ SPEC → TEST(RED) → 実装(GREEN) → REFACTOR → DOC の順序
✅ すべてのテストがPASSしてからコミット
✅ リファクタリング後もテストがPASS

---

## 📚 参考リソース

- **[TDD セットアップガイド](TDD_SETUP.md)** - 詳細な環境構築
- **[CLAUDE.md](../.claude/CLAUDE.md)** - プロジェクトルール全体
- **pytest ドキュメント**: https://docs.pytest.org/

---

**スラッシュコマンドが使えなくても、このガイドに従ってTDDを実践できます！** 🧪✨
