"""
MarkdownExporter ユニットテスト (Builder B)
"""
import re
import pytest
from pathlib import Path

from src.exporter.md_exporter import MarkdownExporter


# ------------------------------------------------------------------
# フィクスチャ
# ------------------------------------------------------------------

@pytest.fixture
def exporter(tmp_path):
    return MarkdownExporter(output_dir=tmp_path)


SAMPLE_POSTS = [
    {
        "id": "111",
        "text": "Python と AI の最新動向",
        "created_at": "2025-01-15T10:00:00Z",
        "author_id": "123",
    },
    {
        "id": "222",
        "text": "今日のランチは<ラーメン>でした！",
        "created_at": "2025-01-14T12:00:00Z",
        "author_id": "123",
    },
]


# ------------------------------------------------------------------
# テスト
# ------------------------------------------------------------------

def test_export_creates_file(exporter, tmp_path):
    filepath = exporter.export(posts=SAMPLE_POSTS, username="testuser")
    assert filepath.exists()
    assert filepath.suffix == ".md"


def test_export_filename_contains_username(exporter):
    filepath = exporter.export(posts=SAMPLE_POSTS, username="myuser")
    assert "myuser" in filepath.name


def test_export_empty_posts(exporter):
    filepath = exporter.export(posts=[], username="testuser")
    content = filepath.read_text(encoding="utf-8")
    assert "条件に一致する投稿はありませんでした" in content


def test_export_content_includes_posts(exporter):
    filepath = exporter.export(posts=SAMPLE_POSTS, username="testuser")
    content = filepath.read_text(encoding="utf-8")
    assert "Python と AI の最新動向" in content
    assert "今日のランチは" in content


def test_export_content_escapes_html(exporter):
    filepath = exporter.export(posts=SAMPLE_POSTS, username="testuser")
    content = filepath.read_text(encoding="utf-8")
    # <ラーメン> が &lt;ラーメン&gt; にエスケープされているか
    assert "<ラーメン>" not in content
    assert "&lt;ラーメン&gt;" in content


def test_export_content_has_metadata(exporter):
    filepath = exporter.export(
        posts=SAMPLE_POSTS,
        username="testuser",
        keyword="Python",
        start_time="2025-01-01T00:00:00Z",
        end_time="2025-01-31T23:59:59Z",
    )
    content = filepath.read_text(encoding="utf-8")
    assert "Python" in content
    assert "2025-01-01T00:00:00Z" in content
    assert "2025-01-31T23:59:59Z" in content


def test_export_contains_post_urls(exporter):
    filepath = exporter.export(posts=SAMPLE_POSTS, username="testuser")
    content = filepath.read_text(encoding="utf-8")
    assert "https://x.com/testuser/status/111" in content


def test_export_count_in_metadata(exporter):
    filepath = exporter.export(posts=SAMPLE_POSTS, username="testuser")
    content = filepath.read_text(encoding="utf-8")
    assert "2 件" in content


def test_safe_name_sanitizes_special_chars(exporter):
    filepath = exporter.export(posts=[], username="user@name!")
    # ファイル名に危険な文字が含まれていないこと
    assert "@" not in filepath.name
    assert "!" not in filepath.name


def test_output_dir_created_if_not_exists(tmp_path):
    new_dir = tmp_path / "nested" / "output"
    exp = MarkdownExporter(output_dir=new_dir)
    assert new_dir.exists()
