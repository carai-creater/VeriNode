"""pytest 初期化: テストでは既定で .env を読まない（ローカルの SERPER 等で期待値がずれるのを防ぐ）。"""

from __future__ import annotations

import os

os.environ.setdefault("DISABLE_DOTENV", "1")
