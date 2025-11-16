# クイックスタートガイド

**最終更新**: 2025-11-16
**現在のフェーズ**: Phase 0準備完了 → データ収集開始可能

---

## 🎉 現在の状態

✅ **完了したこと**:
- プロジェクト全体のフォルダ構成構築（28ディレクトリ、46ファイル）
- Phase 0-3の全スクリプト・テンプレート作成
- 4つのプロジェクトペルソナ作成（Engineer, PM, PO, Blogger）
- 開発日記システム構築
- GitHubリポジトリ作成・初回プッシュ完了

🔗 **GitHubリポジトリ**: https://github.com/almlog/ai-trading-system

---

## 🚀 今すぐ始める（Phase 0）

### Step 1: 環境セットアップ

```bash
# Python仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 依存パッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: 環境変数設定

```bash
# .envファイルの作成
cp .env.example .env

# エディタで.envを編集
notepad .env  # Windows
nano .env     # Mac/Linux
```

**必須のAPIキー**:
- `KAGGLE_USERNAME`: Kaggleユーザー名
- `KAGGLE_KEY`: Kaggle APIキー
- `ANTHROPIC_API_KEY`: Claude APIキー

### Step 3: Kaggle API設定

```bash
# Windows
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# Mac/Linux
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 4: Phase 0セットアップ

```bash
# NLTKデータのダウンロード等
make phase0-setup

# または手動で
python -m nltk.downloader vader_lexicon
python -m nltk.downloader punkt
```

### Step 5: データ収集

```bash
# Kaggleデータセットのダウンロード
make phase0-download-data

# または手動で
python phase0_data_analysis/scripts/download_kaggle_data.py
```

### Step 6: パターン発見

```bash
# AI分析実行
make phase0-analyze

# または手動で
python phase0_data_analysis/scripts/pattern_discovery.py
```

### Step 7: 検証

```bash
# パターンの検証
make phase0-validate

# または手動で
python phase0_data_analysis/scripts/validate_patterns.py
```

---

## 📝 開発日記の書き方

### 毎日の記録

```bash
# 今日の日付でファイル作成
cp devlog/TEMPLATE.md devlog/$(date +%Y-%m-%d).md

# Windows PowerShellの場合
cp devlog/TEMPLATE.md devlog/$(Get-Date -Format yyyy-MM-dd).md

# エディタで編集
notepad devlog/2025-11-17.md
```

### 15分ルール

- 完璧を目指さない
- 箇条書きOK
- 感情も記録
- ハマったポイントは詳細に

---

## 🎭 ペルソナの使い分け

### いつ誰に聞くか

| 質問の種類 | ペルソナ | 起動フレーズ |
|-----------|---------|-------------|
| 技術実装の詳細 | Engineer | `@engineer` |
| 優先度・スケジュール | PM | `@pm` |
| ビジョン・価値判断 | PO | `@po` |
| ブログ記事・学び | Blogger | `@blogger` |

### 例

```
# 技術的な質問
"@engineer Lambda関数のタイムアウト設定は？"

# 優先度の相談
"@pm この機能をPhase 0に追加すべき？"

# ビジョン確認
"@po そもそもこのプロジェクトの目的は？"

# ブログ記事
"@blogger 今週の学びをQiita記事にまとめたい"
```

---

## 📊 Phase 0の成功基準

- [ ] `patterns_v1.json` が生成されている
- [ ] パターン数が5個以上
- [ ] 各パターンのサンプル数が10件以上
- [ ] `phase0_report.md` が作成されている
- [ ] 分析プロセスが文書化されている

---

## 🔄 Git ワークフロー

### 日々の作業

```bash
# 作業開始時
git pull origin main

# こまめにコミット
git add .
git commit -m "feat(phase0): implement feature extraction"

# 作業終了時
git push origin main
```

### フィーチャーブランチ（オプション）

```bash
# Phase 0用ブランチ作成
git checkout -b feature/phase0-pattern-discovery

# 作業完了後
git checkout main
git merge feature/phase0-pattern-discovery
git push origin main
```

---

## 🆘 トラブルシューティング

### Kaggle APIが動かない

```bash
# Kaggle認証情報を確認
ls ~/.kaggle/kaggle.json  # Mac/Linux
dir %USERPROFILE%\.kaggle\kaggle.json  # Windows

# 権限を確認（Mac/Linux）
chmod 600 ~/.kaggle/kaggle.json
```

### NLTK データが見つからない

```bash
# Python対話モードで
python
>>> import nltk
>>> nltk.download('vader_lexicon')
>>> nltk.download('punkt')
```

### 仮想環境が有効化されない

```bash
# Windows: PowerShellの実行ポリシー変更が必要な場合
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# その後再度
venv\Scripts\activate
```

---

## 📚 次に読むべきドキュメント

### 詳細な手順
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 完全な環境構築手順

### Phase 0の詳細
- **[phase0_data_analysis/README.md](../phase0_data_analysis/README.md)** - Phase 0ガイド

### プロジェクト管理
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - 現在の進捗状況
- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - GitHub管理方法

### ペルソナ
- **[personas/README.md](../personas/README.md)** - ペルソナ概要

---

## 💡 開発のヒント

### 育児との両立

- **朝**: 子供が寝ている間に30分
- **昼**: 昼寝中に1-2時間（運が良ければ）
- **夜**: 寝かしつけ後に1時間

→ 合計2-3時間/日が目安

### 焦らない

- Phase 0は2週間が目安
- 毎日進めなくてもOK
- システムは自律動作設計（Phase 1以降）

### 楽しむ

- 学びをdevlogに記録
- 小さな成功を祝う
- コミュニティ（Qiita）に発信

---

## 🎯 今週の目標（Week 1）

- [ ] 環境セットアップ完了
- [ ] Kaggleデータセット取得
- [ ] 最初の特徴量抽出
- [ ] devlogを3日以上記録

---

**Let's start Phase 0!** 🚀

---

## 📞 サポート

質問・問題がある場合:
1. 各ディレクトリのREADME.mdを確認
2. SETUP_GUIDE.mdのトラブルシューティング参照
3. ペルソナに相談（@engineer, @pm, @po, @blogger）
