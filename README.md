# X投稿取得ツール

指定したXアカウントの投稿を取得し、Markdownファイルとして保存するツール。

## セットアップ

```bash
# 1. 依存パッケージをインストール
python -m pip install -r requirements.txt

# 2. 環境変数ファイルを作成
cp .env.example .env
# .env を開いて X_BEARER_TOKEN を入力
```

> **重要:** `.env` の内容を絶対にチャット・Git・共有ストレージに貼り付けないこと。

## 使い方

```bash
python -X utf8 -m src.main --username <ユーザー名> [オプション]
```

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--username` | X ユーザー名（必須） | `elonmusk` |
| `--keyword` | フィルタキーワード | `"Python"` |
| `--start-time` | 取得開始日時（ISO8601） | `2025-01-01T00:00:00Z` |
| `--end-time` | 取得終了日時（ISO8601） | `2025-01-31T23:59:59Z` |
| `--max-results` | 最大取得件数（1〜500） | `50` |

出力先: `output/posts/<username>_<timestamp>.md`

## テスト実行

```bash
python -m pytest tests/ -v
```

## ディレクトリ構成

```
├── .env.example       # 環境変数テンプレート（値なし）
├── requirements.txt
├── src/
│   ├── fetcher/       # X API v2 投稿取得
│   ├── exporter/      # Markdown出力
│   └── main.py        # CLIエントリーポイント
├── tests/
└── output/posts/      # .md ファイル出力先
```
