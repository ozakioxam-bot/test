"""
X投稿取得モジュール (Builder A)

X API v2 を使用して、指定アカウントの投稿を取得する。
- アカウント指定（username）
- 期間指定（start_time / end_time）
- キーワードフィルタリング（keyword）
"""
import os
import time
import requests
from datetime import datetime, timezone
from typing import Optional


X_API_BASE = "https://api.twitter.com/2"


class XFetcherError(Exception):
    pass


class XFetcher:
    def __init__(self, bearer_token: str):
        if not bearer_token:
            raise XFetcherError("Bearer Tokenが設定されていません。.envを確認してください。")
        self._headers = {"Authorization": f"Bearer {bearer_token}"}

    # ------------------------------------------------------------------
    # 公開メソッド
    # ------------------------------------------------------------------

    def fetch_posts(
        self,
        username: str,
        keyword: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_results: int = 100,
    ) -> list[dict]:
        """
        指定ユーザーの投稿を取得する。

        Args:
            username: Xのユーザー名（@なし）
            keyword: フィルタするキーワード（Noneで全件）
            start_time: 開始日時（ISO 8601、例: "2025-01-01T00:00:00Z"）
            end_time: 終了日時（ISO 8601）
            max_results: 最大取得件数（5〜500）

        Returns:
            投稿データのリスト（dictのリスト）
        """
        if not username:
            raise XFetcherError("usernameを指定してください。")
        if not (5 <= max_results <= 500):
            raise XFetcherError("max_resultsは5〜500の範囲で指定してください。")

        user_id = self._get_user_id(username)
        posts = self._get_timeline(
            user_id=user_id,
            keyword=keyword,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results,
        )
        return posts

    # ------------------------------------------------------------------
    # 内部メソッド
    # ------------------------------------------------------------------

    def _get_user_id(self, username: str) -> str:
        url = f"{X_API_BASE}/users/by/username/{username}"
        response = self._request("GET", url)
        data = response.get("data")
        if not data:
            raise XFetcherError(f"ユーザー '{username}' が見つかりません。")
        return data["id"]

    def _get_timeline(
        self,
        user_id: str,
        keyword: Optional[str],
        start_time: Optional[str],
        end_time: Optional[str],
        max_results: int,
    ) -> list[dict]:
        url = f"{X_API_BASE}/users/{user_id}/tweets"
        # 1回のリクエストで取得できる上限は100件
        per_page = min(max_results, 100)
        params: dict = {
            "max_results": per_page,
            "tweet.fields": "created_at,text,author_id,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name",
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        all_posts: list[dict] = []
        next_token: Optional[str] = None

        while len(all_posts) < max_results:
            if next_token:
                params["pagination_token"] = next_token
            else:
                params.pop("pagination_token", None)

            response = self._request("GET", url, params=params)
            posts_page = response.get("data", [])
            if not posts_page:
                break

            # キーワードフィルタ（APIクエリではなくローカルフィルタ）
            if keyword:
                kw = keyword.lower()
                posts_page = [p for p in posts_page if kw in p.get("text", "").lower()]

            all_posts.extend(posts_page)

            meta = response.get("meta", {})
            next_token = meta.get("next_token")
            if not next_token or len(all_posts) >= max_results:
                break

            # レート制限への配慮
            time.sleep(1)

        return all_posts[:max_results]

    def _request(self, method: str, url: str, **kwargs) -> dict:
        try:
            resp = requests.request(
                method, url, headers=self._headers, timeout=30, **kwargs
            )
        except requests.RequestException as e:
            raise XFetcherError(f"APIリクエスト失敗: {e}") from e

        if resp.status_code == 401:
            raise XFetcherError("Bearer Tokenが無効です。.envのX_BEARER_TOKENを確認してください。")
        if resp.status_code == 429:
            raise XFetcherError("X APIのレート制限に達しました。しばらく時間をおいて再試行してください。")
        if not resp.ok:
            raise XFetcherError(f"X API エラー {resp.status_code}: {resp.text[:200]}")

        return resp.json()


def load_fetcher() -> XFetcher:
    """環境変数からBearer Tokenを読み込んでXFetcherを返す。"""
    token = os.environ.get("X_BEARER_TOKEN", "")
    if not token:
        raise XFetcherError(
            "環境変数 X_BEARER_TOKEN が設定されていません。\n"
            ".env.example をコピーして .env を作成し、値を入力してください。"
        )
    return XFetcher(bearer_token=token)
