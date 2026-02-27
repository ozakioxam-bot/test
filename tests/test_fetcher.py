"""
XFetcher ユニットテスト (Builder A)
外部API呼び出しはモックで代替する。
"""
import pytest
from unittest.mock import MagicMock, patch

from src.fetcher.x_fetcher import XFetcher, XFetcherError, load_fetcher


# ------------------------------------------------------------------
# フィクスチャ
# ------------------------------------------------------------------

@pytest.fixture
def fetcher():
    return XFetcher(bearer_token="dummy_token")


MOCK_USER_RESPONSE = {"data": {"id": "123456", "username": "testuser"}}

MOCK_TIMELINE_RESPONSE = {
    "data": [
        {
            "id": "1",
            "text": "Python と AI の話題",
            "created_at": "2025-01-15T10:00:00Z",
            "author_id": "123456",
        },
        {
            "id": "2",
            "text": "今日のランチ",
            "created_at": "2025-01-14T12:00:00Z",
            "author_id": "123456",
        },
    ],
    "meta": {"result_count": 2},
}


# ------------------------------------------------------------------
# 初期化テスト
# ------------------------------------------------------------------

def test_init_raises_on_empty_token():
    with pytest.raises(XFetcherError, match="Bearer Token"):
        XFetcher(bearer_token="")


def test_init_success():
    f = XFetcher(bearer_token="valid_token")
    assert f is not None


# ------------------------------------------------------------------
# fetch_posts テスト
# ------------------------------------------------------------------

def test_fetch_posts_validates_username(fetcher):
    with pytest.raises(XFetcherError, match="username"):
        fetcher.fetch_posts(username="")


def test_fetch_posts_validates_max_results(fetcher):
    with pytest.raises(XFetcherError, match="max_results"):
        fetcher.fetch_posts(username="testuser", max_results=0)
    with pytest.raises(XFetcherError, match="max_results"):
        fetcher.fetch_posts(username="testuser", max_results=501)


def test_fetch_posts_success(fetcher):
    with patch.object(fetcher, "_request") as mock_req:
        mock_req.side_effect = [MOCK_USER_RESPONSE, MOCK_TIMELINE_RESPONSE]
        posts = fetcher.fetch_posts(username="testuser")
    assert len(posts) == 2
    assert posts[0]["text"] == "Python と AI の話題"


def test_fetch_posts_keyword_filter(fetcher):
    with patch.object(fetcher, "_request") as mock_req:
        mock_req.side_effect = [MOCK_USER_RESPONSE, MOCK_TIMELINE_RESPONSE]
        posts = fetcher.fetch_posts(username="testuser", keyword="Python")
    assert len(posts) == 1
    assert "Python" in posts[0]["text"]


def test_fetch_posts_user_not_found(fetcher):
    with patch.object(fetcher, "_request") as mock_req:
        mock_req.return_value = {}
        with pytest.raises(XFetcherError, match="見つかりません"):
            fetcher.fetch_posts(username="nonexistent")


# ------------------------------------------------------------------
# エラーハンドリングテスト
# ------------------------------------------------------------------

def test_request_401_raises(fetcher):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.ok = False
    with patch("requests.request", return_value=mock_resp):
        with pytest.raises(XFetcherError, match="Bearer Token"):
            fetcher._request("GET", "https://api.twitter.com/2/users/by/username/test")


def test_request_429_raises(fetcher):
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.ok = False
    with patch("requests.request", return_value=mock_resp):
        with pytest.raises(XFetcherError, match="レート制限"):
            fetcher._request("GET", "https://api.twitter.com/2/users/by/username/test")


# ------------------------------------------------------------------
# load_fetcher テスト
# ------------------------------------------------------------------

def test_load_fetcher_missing_env(monkeypatch):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    with pytest.raises(XFetcherError, match="X_BEARER_TOKEN"):
        load_fetcher()


def test_load_fetcher_success(monkeypatch):
    monkeypatch.setenv("X_BEARER_TOKEN", "test_token")
    f = load_fetcher()
    assert isinstance(f, XFetcher)
