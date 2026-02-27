"""
Flask WebサーバーモジュールX投稿取得ツールをブラウザから操作できるWebUIを提供する。
- GET  /                 : フォームUI
- POST /fetch            : 投稿取得 → MD生成 → JSON返却
- GET  /download/<name>  : 生成済みMDファイルのダウンロード
"""
import sys
from pathlib import Path

# プロジェクトルートをモジュール検索パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, render_template, send_file, abort
from dotenv import load_dotenv

from src.fetcher.x_fetcher import load_fetcher, XFetcherError
from src.exporter.md_exporter import MarkdownExporter

load_dotenv()

app = Flask(__name__)

# 出力ディレクトリ（絶対パスで固定）
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "posts"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/fetch", methods=["POST"])
def fetch():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip().lstrip("@")
    keyword = (data.get("keyword") or "").strip() or None
    start_time = (data.get("start_time") or "").strip() or None
    end_time = (data.get("end_time") or "").strip() or None

    try:
        max_results = int(data.get("max_results") or 50)
    except (ValueError, TypeError):
        return jsonify({"error": "max_resultsは整数で指定してください。"}), 400

    if not username:
        return jsonify({"error": "usernameを指定してください。"}), 400

    try:
        fetcher = load_fetcher()
        posts = fetcher.fetch_posts(
            username=username,
            keyword=keyword,
            start_time=start_time,
            end_time=end_time,
            max_results=max_results,
        )
    except XFetcherError as e:
        return jsonify({"error": str(e)}), 400

    exporter = MarkdownExporter(output_dir=OUTPUT_DIR)
    filepath = exporter.export(
        posts=posts,
        username=username,
        keyword=keyword,
        start_time=start_time,
        end_time=end_time,
    )

    return jsonify({"count": len(posts), "filename": filepath.name})


@app.route("/download/<filename>")
def download(filename):
    # パストラバーサル防止: ディレクトリ成分を除去してファイル名のみ使用
    safe_name = Path(filename).name
    filepath = OUTPUT_DIR / safe_name

    # OUTPUT_DIR の外を指すパスを拒否
    try:
        filepath.resolve().relative_to(OUTPUT_DIR.resolve())
    except ValueError:
        abort(400)

    if not filepath.is_file():
        abort(404)

    return send_file(filepath, as_attachment=True, download_name=safe_name)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=False, host="127.0.0.1", port=5000)
