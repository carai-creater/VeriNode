"""
VeriNode — 本番・Vercel 用エントリポイント。

Vercel はリポジトリ直下の server.py 内の `app` を検出する。
ローカルは従来どおり `uvicorn app.main:app` でも可。
"""

from app.main import app

__all__ = ["app"]
