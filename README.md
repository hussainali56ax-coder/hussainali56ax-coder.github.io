# Telegram E-Commerce Bot - ChatGPT GO Codes

A modern Telegram storefront bot to sell **ChatGPT GO (3 Months)** codes with:

- Emoji-rich storefront UI and inline buttons.
- Custom title, description, and image from environment settings.
- Admin panel protected by `ADMIN_ID`.
- Dual payment methods:
  - Telegram Stars
  - Binance Pay (ID configurable, default `866451330`)
- Payment verification flow: customer submits "I Paid - Verify", admin gets notified before code delivery.
- Item management with flexible catalog (`/additem`) including both USDT and Stars pricing.
- Order persistence in `orders.json`.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Update BOT_TOKEN and ADMIN_ID at minimum
python bot.py
```

## Commands

- `/start` Show storefront.
- `/additem` (admin only) Add a new product with USDT + Stars price.
- `/cancel` Cancel add-item flow.

## Notes

- Price control is fully managed by admin when adding items.
- Buyers are not auto-delivered codes until admin verifies payment.
- You can add more products anytime from the bot or by editing `items.json`.
