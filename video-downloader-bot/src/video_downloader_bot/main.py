from __future__ import annotations

import logging

from dotenv import load_dotenv

from .config import load_settings
from .telegram_bot import build_application


def main() -> None:
    load_dotenv()
    settings = load_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    logging.getLogger(__name__).info("Starting bot with download dir: %s", settings.download_dir)
    app = build_application(settings)
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
