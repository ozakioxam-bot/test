"""
デモスクリプト — X APIキー不要でツールの動作を確認できます。

実行方法:
    python demo.py
"""
import sys
import io

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MOCK_POSTS = [
    {
        "id": "1001",
        "text": "Pythonの新機能が発表されました！型ヒントの改善とパフォーマンス向上が目玉です。#Python #AI",
        "created_at": "2025-01-15T09:00:00Z",
        "author_id": "demo_user",
    },
    {
        "id": "1002",
        "text": "AI × 業務自動化のトレンドが加速中。今年はエージェント型AIが主流になりそうです。#生成AI #業務効率化",
        "created_at": "2025-01-14T14:30:00Z",
        "author_id": "demo_user",
    },
    {
        "id": "1003",
        "text": "X API v2の取得制限について整理しました。無料プランでは月1500ツイートまで読み取り可能。#XAPI",
        "created_at": "2025-01-13T10:00:00Z",
        "author_id": "demo_user",
    },
]


def main():
    print("=" * 60)
    print("X投稿取得ツール — デモ実行")
    print("=" * 60)
    print()

    from src.exporter.md_exporter import MarkdownExporter

    print("Markdownファイルを生成中...")
    exporter = MarkdownExporter()
    md_path = exporter.export(
        posts=MOCK_POSTS,
        username="demo_account",
        keyword="Python",
        start_time="2025-01-01T00:00:00Z",
        end_time="2025-01-31T23:59:59Z",
    )
    print(f"  → 出力完了: {md_path}")
    print()
    print("実際のX APIに接続する場合:")
    print("  1. .env に X_BEARER_TOKEN を設定")
    print("  2. python -X utf8 -m src.main --username <アカウント名>")
    print("=" * 60)


if __name__ == "__main__":
    main()
