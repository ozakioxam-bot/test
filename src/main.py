"""
X投稿取得・自動配信ツール — CLIエントリーポイント

使用方法:
    python -m src.main fetch --username <username> [options]

環境変数（.env に設定）:
    X_BEARER_TOKEN : X API v2 Bearer Token（必須）
"""
import argparse
import sys
import io
from pathlib import Path

# Windows端末での日本語文字化けを防ぐ
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

from src.fetcher.x_fetcher import XFetcherError, load_fetcher
from src.exporter.md_exporter import MarkdownExporter


def cmd_fetch(args: argparse.Namespace) -> int:
    try:
        fetcher = load_fetcher()
    except XFetcherError as e:
        print(f"[エラー] {e}", file=sys.stderr)
        return 1

    print(f"[1/2] @{args.username} の投稿を取得中...")
    try:
        posts = fetcher.fetch_posts(
            username=args.username,
            keyword=args.keyword,
            start_time=args.start_time,
            end_time=args.end_time,
            max_results=args.max_results,
        )
    except XFetcherError as e:
        print(f"[エラー] {e}", file=sys.stderr)
        return 1

    print(f"  → {len(posts)} 件取得しました。")

    print("[2/2] Markdownファイルを生成中...")
    exporter = MarkdownExporter()
    md_path = exporter.export(
        posts=posts,
        username=args.username,
        keyword=args.keyword,
        start_time=args.start_time,
        end_time=args.end_time,
    )
    print(f"  → 出力完了: {md_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="x-delivery-tool",
        description="X投稿取得ツール — 指定アカウントの投稿をMarkdownで保存します",
    )
    parser.add_argument("--username", required=True, help="X ユーザー名（@なし）")
    parser.add_argument("--keyword", default=None, help="フィルタキーワード")
    parser.add_argument("--start-time", dest="start_time", default=None,
                        help="取得開始日時 ISO8601（例: 2025-01-01T00:00:00Z）")
    parser.add_argument("--end-time", dest="end_time", default=None,
                        help="取得終了日時 ISO8601")
    parser.add_argument("--max-results", dest="max_results", type=int, default=100,
                        help="最大取得件数（1〜500、デフォルト: 100）")
    return parser


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    return cmd_fetch(args)


if __name__ == "__main__":
    sys.exit(main())
