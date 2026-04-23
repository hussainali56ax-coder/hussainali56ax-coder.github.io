# Video Downloader Bot (Telegram-first)

Cross-platform video downloader starter project built around `yt-dlp`.

> Platform support is as broad as `yt-dlp` extractor support (YouTube, TikTok, Instagram, X/Twitter, Facebook, and many more).

## Features

- Accepts user-sent URLs in Telegram chat
- Validates URL format before processing
- Checks extractor support and handles unsupported links gracefully
- Downloads with a practical size strategy for messaging use
- Sends video back to user and removes local temp file after upload
- Modular structure: reusable downloader core + Telegram interface layer
- Environment-variable configuration (no hardcoded secrets)
- Basic logging and error handling

## Project layout

```text
video-downloader-bot/
├── src/video_downloader_bot/
│   ├── config.py
│   ├── downloader.py
│   ├── telegram_bot.py
│   └── main.py
├── .env.example
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

## Requirements

- Python 3.10+
- `ffmpeg` installed on host (for some merged formats)

## Setup

```bash
cd /home/runner/work/hussainali56ax-coder.github.io/hussainali56ax-coder.github.io/video-downloader-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

Set your bot token in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_real_token
MAX_DOWNLOAD_SIZE_MB=49
DOWNLOAD_DIR=./downloads
LOG_LEVEL=INFO
```

## Run

```bash
cd /home/runner/work/hussainali56ax-coder.github.io/hussainali56ax-coder.github.io/video-downloader-bot
source .venv/bin/activate
python -m video_downloader_bot.main
```

## Docker

```bash
cd /home/runner/work/hussainali56ax-coder.github.io/hussainali56ax-coder.github.io/video-downloader-bot
docker build -t video-downloader-bot .
docker run --rm -e TELEGRAM_BOT_TOKEN=your_real_token video-downloader-bot
```

## Notes and limits

- If a platform changes, extractor support may temporarily break until upstream `yt-dlp` updates.
- Very large videos may be rejected due to `MAX_DOWNLOAD_SIZE_MB`.
- Some websites may block content by region/account/age.
