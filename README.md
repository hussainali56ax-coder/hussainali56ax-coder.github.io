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

## Quick VPS Start (one command)

Use this command inside your VPS after cloning the repo:

```bash
bash deploy_vps.sh '8498047282:AAHQvbUQdCqxl_Ds5yYPumVm2X5HfiRV6sE' '779770071'
```

This will:

1. Create virtual environment
2. Install dependencies
3. Generate `.env`
4. Run the bot in background

Check logs:

```bash
tail -f bot.log
```

## Manual Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set BOT_TOKEN and ADMIN_ID
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
