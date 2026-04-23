from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .config import Settings
from .downloader import (
    DownloaderError,
    FileTooLargeError,
    InvalidUrlError,
    UnsupportedUrlError,
    VideoDownloader,
)

logger = logging.getLogger(__name__)


def build_application(settings: Settings) -> Application:
    downloader = VideoDownloader(
        download_dir=settings.download_dir,
        max_size_bytes=settings.max_download_size_bytes,
    )

    application = Application.builder().token(settings.telegram_bot_token).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        await update.message.reply_text(
            "Welcome 👋\n"
            "Send any video URL and I will try to download it using yt-dlp extractors.\n"
            f"Current file-size limit: {settings.max_download_size_mb} MB."
        )

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        await update.message.reply_text(
            "Usage:\n"
            "- Send a direct video page/link URL.\n"
            "- I support many platforms through yt-dlp.\n"
            "- If a link is unsupported/unavailable, I will tell you clearly."
        )

    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        message = update.message
        if not message or not message.text:
            return

        url = message.text.strip()
        status = await message.reply_text("⏳ Checking URL and downloading...")
        result = None
        try:
            result = await downloader.download_video(url)
            await status.edit_text(
                f"✅ Downloaded from `{result.source_platform}`.\nUploading...",
                parse_mode="Markdown",
            )
            await message.chat.send_action(action=ChatAction.UPLOAD_VIDEO)
            with result.file_path.open("rb") as video_file:
                await message.reply_video(video=video_file, caption=result.title[:1024])
            await status.delete()
        except InvalidUrlError as exc:
            await status.edit_text(f"❌ {exc}")
        except UnsupportedUrlError as exc:
            await status.edit_text(f"❌ {exc}")
        except FileTooLargeError as exc:
            await status.edit_text(f"⚠️ {exc}")
        except DownloaderError:
            await status.edit_text("❌ Download failed. The source may block downloads right now.")
        except Exception:
            logger.exception("Unhandled error while processing user message")
            await status.edit_text("❌ Unexpected error. Please try again later.")
        finally:
            if result:
                result.file_path.unlink(missing_ok=True)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return application
