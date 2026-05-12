#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <BOT_TOKEN> <ADMIN_ID>"
  exit 1
fi

BOT_TOKEN="$1"
ADMIN_ID="$2"
BINANCE_ID="${3:-866451330}"

cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cat > .env <<EOF
BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}
BOT_TITLE=GPT GO CODES SHOP
BOT_DESCRIPTION=Premium ChatGPT GO 3-Month Code Store
BOT_IMAGE=https://images.unsplash.com/photo-1518773553398-650c184e0bb3
BINANCE_ID=${BINANCE_ID}
EOF

pkill -f "python bot.py" || true
nohup .venv/bin/python bot.py > bot.log 2>&1 &
echo "Bot started in background. Logs: tail -f bot.log"
