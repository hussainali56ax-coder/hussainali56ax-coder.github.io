from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    max_download_size_mb: int
    download_dir: Path
    log_level: str

    @property
    def max_download_size_bytes(self) -> int:
        return self.max_download_size_mb * 1024 * 1024


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")

    size_mb = int(os.getenv("MAX_DOWNLOAD_SIZE_MB", "49"))
    if size_mb <= 0:
        raise ValueError("MAX_DOWNLOAD_SIZE_MB must be greater than zero")

    download_dir = Path(os.getenv("DOWNLOAD_DIR", "./downloads")).resolve()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    return Settings(
        telegram_bot_token=token,
        max_download_size_mb=size_mb,
        download_dir=download_dir,
        log_level=log_level,
    )
