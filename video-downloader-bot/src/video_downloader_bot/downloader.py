from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp

logger = logging.getLogger(__name__)


class DownloaderError(Exception):
    pass


class InvalidUrlError(DownloaderError):
    pass


class UnsupportedUrlError(DownloaderError):
    pass


class FileTooLargeError(DownloaderError):
    pass


@dataclass(frozen=True)
class DownloadResult:
    file_path: Path
    title: str
    source_platform: str


class VideoDownloader:
    def __init__(self, download_dir: Path, max_size_bytes: int) -> None:
        self.download_dir = download_dir
        self.max_size_bytes = max_size_bytes
        self.download_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def is_valid_url(text: str) -> bool:
        parsed = urlparse(text.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    async def download_video(self, url: str) -> DownloadResult:
        if not self.is_valid_url(url):
            raise InvalidUrlError("Please send a valid URL that starts with http:// or https://")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._download_sync, url)

    def _download_sync(self, url: str) -> DownloadResult:
        probe_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
        }
        try:
            with yt_dlp.YoutubeDL(probe_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as exc:
            logger.warning("Unsupported or unavailable URL: %s", url)
            raise UnsupportedUrlError(
                "This URL is unsupported or currently unavailable with yt-dlp extractors."
            ) from exc

        title = (info.get("title") or "video").strip()
        source_platform = info.get("extractor_key") or info.get("extractor") or "unknown"
        max_size = self.max_size_bytes

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "restrictfilenames": True,
            "retries": 3,
            "outtmpl": str(self.download_dir / "%(title).80B-%(id)s.%(ext)s"),
            "merge_output_format": "mp4",
            "format": f"bv*+ba/b[filesize<{max_size}]/b",
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = self._resolve_downloaded_path(ydl, info)
        except yt_dlp.utils.DownloadError as exc:
            logger.exception("Download failed for URL: %s", url)
            raise DownloaderError("Failed to download this video. Try another link or a lower quality.") from exc

        file_size = file_path.stat().st_size
        if file_size > max_size:
            file_path.unlink(missing_ok=True)
            raise FileTooLargeError(
                f"Downloaded file is too large ({round(file_size / 1024 / 1024, 1)} MB). "
                f"Current limit is {round(max_size / 1024 / 1024)} MB."
            )

        return DownloadResult(file_path=file_path, title=title, source_platform=source_platform)

    @staticmethod
    def _resolve_downloaded_path(ydl: yt_dlp.YoutubeDL, info: dict) -> Path:
        requested = info.get("requested_downloads") or []
        if requested and requested[0].get("filepath"):
            path = Path(requested[0]["filepath"]).resolve()
            if path.exists():
                return path

        candidate = Path(ydl.prepare_filename(info)).resolve()
        if candidate.exists():
            return candidate

        base_name = candidate.stem
        matches = sorted(candidate.parent.glob(f"{base_name}.*"))
        if not matches:
            raise DownloaderError("Download finished but file path could not be resolved.")
        return matches[0].resolve()
