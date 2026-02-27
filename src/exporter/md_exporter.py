"""
Markdown出力モジュール (Builder B)

取得したX投稿データをMarkdown形式のファイルに出力する。
出力先: output/posts/<username>_<timestamp>.md
"""
import os
import re
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_BASE = Path("output/posts")


class MarkdownExporter:
    def __init__(self, output_dir: str | Path = OUTPUT_BASE):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        posts: list[dict],
        username: str,
        keyword: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> Path:
        """
        投稿リストをMarkdownファイルに出力する。

        Args:
            posts: 投稿データのリスト（x_fetcher.fetch_postsの戻り値）
            username: 対象ユーザー名
            keyword: フィルタキーワード（メタ情報として記録）
            start_time: 取得期間の開始（メタ情報として記録）
            end_time: 取得期間の終了（メタ情報として記録）

        Returns:
            出力したMarkdownファイルのPath
        """
        now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"{self._safe_name(username)}_{now}.md"
        filepath = self.output_dir / filename

        content = self._render(
            posts=posts,
            username=username,
            keyword=keyword,
            start_time=start_time,
            end_time=end_time,
            generated_at=now,
        )
        filepath.write_text(content, encoding="utf-8")
        return filepath

    # ------------------------------------------------------------------
    # 内部メソッド
    # ------------------------------------------------------------------

    def _render(
        self,
        posts: list[dict],
        username: str,
        keyword: str | None,
        start_time: str | None,
        end_time: str | None,
        generated_at: str,
    ) -> str:
        lines: list[str] = []

        # ヘッダー
        lines.append(f"# @{self._escape_md(username)} 投稿レポート")
        lines.append("")
        lines.append("## 取得条件")
        lines.append("")
        lines.append(f"| 項目 | 値 |")
        lines.append(f"|------|----|")
        lines.append(f"| アカウント | @{self._escape_md(username)} |")
        lines.append(f"| キーワード | {self._escape_md(keyword or '（指定なし）')} |")
        lines.append(f"| 開始日時 | {self._escape_md(start_time or '（指定なし）')} |")
        lines.append(f"| 終了日時 | {self._escape_md(end_time or '（指定なし）')} |")
        lines.append(f"| 取得件数 | {len(posts)} 件 |")
        lines.append(f"| 生成日時 | {generated_at} |")
        lines.append("")

        if not posts:
            lines.append("## 投稿一覧")
            lines.append("")
            lines.append("_条件に一致する投稿はありませんでした。_")
            return "\n".join(lines)

        # 投稿一覧
        lines.append("## 投稿一覧")
        lines.append("")
        for i, post in enumerate(posts, start=1):
            text = post.get("text", "")
            created = post.get("created_at", "")
            post_id = post.get("id", "")

            lines.append(f"### {i}. {self._escape_md(self._truncate(text, 60))}")
            lines.append("")
            if created:
                lines.append(f"**日時:** {self._escape_md(created)}")
                lines.append("")
            lines.append(self._escape_md(text))
            lines.append("")
            if post_id:
                url = f"https://x.com/{username}/status/{post_id}"
                lines.append(f"[元の投稿を見る]({url})")
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _escape_md(text: str) -> str:
        """Markdownの特殊文字をエスケープする（XSS防止・表示崩れ防止）。"""
        # テーブルセル内のパイプ文字を エスケープ
        return text.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")

    @staticmethod
    def _truncate(text: str, length: int) -> str:
        return text[:length] + ("..." if len(text) > length else "")

    @staticmethod
    def _safe_name(name: str) -> str:
        """ファイル名として安全な文字列に変換する。"""
        return re.sub(r"[^\w\-]", "_", name)[:50]
