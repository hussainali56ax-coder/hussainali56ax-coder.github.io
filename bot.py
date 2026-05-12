import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_TITLE = os.getenv("BOT_TITLE", "GPT GO CODES SHOP")
BOT_DESCRIPTION = os.getenv("BOT_DESCRIPTION", "Premium ChatGPT GO code store")
BOT_IMAGE = os.getenv("BOT_IMAGE", "")
BINANCE_ID = os.getenv("BINANCE_ID", "866451330")

ITEMS_FILE = Path("items.json")
ORDERS_FILE = Path("orders.json")

ADD_ITEM_NAME, ADD_ITEM_USDT, ADD_ITEM_STARS, ADD_ITEM_DESC = range(4)
SET_USDT, SET_STARS = range(100, 102)


def _ensure_files() -> None:
    if not ITEMS_FILE.exists():
        ITEMS_FILE.write_text(
            json.dumps(
                [
                    {
                        "id": "gptgo3m",
                        "name": "ChatGPT GO - 3 Months",
                        "price_usdt": 9.99,
                        "price_stars": 450,
                        "description": "3-month subscription code with instant delivery after payment verification.",
                        "emoji": "🚀",
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    if not ORDERS_FILE.exists():
        ORDERS_FILE.write_text("[]", encoding="utf-8")


def _load_items() -> list[dict]:
    return json.loads(ITEMS_FILE.read_text(encoding="utf-8"))


def _save_items(items: list[dict]) -> None:
    ITEMS_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_orders() -> list[dict]:
    return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))


def _save_orders(orders: list[dict]) -> None:
    ORDERS_FILE.write_text(json.dumps(orders, ensure_ascii=False, indent=2), encoding="utf-8")


def _menu_keyboard(items: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                f"{i['emoji']} {i['name']} — {i['price_usdt']} USDT / {i['price_stars']} ⭐",
                callback_data=f"buy:{i['id']}",
            )
        ]
        for i in items
    ]
    rows.append([InlineKeyboardButton("🛠 Admin Panel", callback_data="admin")])
    return InlineKeyboardMarkup(rows)


def _payment_keyboard(item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⭐ Pay with Telegram Stars", callback_data=f"pay:stars:{item_id}")],
            [InlineKeyboardButton("🟡 Pay with Binance USDT", callback_data=f"pay:binance:{item_id}")],
            [InlineKeyboardButton("✅ I Paid - Verify", callback_data=f"verify:{item_id}")],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ensure_files()
    items = _load_items()
    caption = (
        f"🎨 <b>{BOT_TITLE}</b>\n"
        f"{BOT_DESCRIPTION}\n\n"
        "⚡ Fast code delivery after payment confirmation\n"
        "💳 Payment: Telegram Stars or Binance USDT\n"
        "👇 Select a product to start"
    )

    if BOT_IMAGE:
        await update.message.reply_photo(
            BOT_IMAGE,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=_menu_keyboard(items),
        )
    else:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML, reply_markup=_menu_keyboard(items))


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "admin":
        if q.from_user.id != ADMIN_ID:
            await q.message.reply_text("⛔ Admin access only.")
            return
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("➕ Add Item", callback_data="admin:add")],
                [InlineKeyboardButton("📦 List Items", callback_data="admin:list")],
            ]
        )
        await q.message.reply_text("👑 Admin dashboard:", reply_markup=kb)
        return

    if data == "admin:list" and q.from_user.id == ADMIN_ID:
        items = _load_items()
        rows = []
        for x in items:
            rows.append(
                f"• {x['emoji']} {x['name']}\n"
                f"  Price: {x['price_usdt']} USDT / {x['price_stars']} ⭐\n"
                f"  {x['description']}"
            )
        await q.message.reply_text("📋 Current items:\n\n" + "\n\n".join(rows))
        return

    if data == "admin:add":
        if q.from_user.id != ADMIN_ID:
            await q.message.reply_text("⛔ Not allowed.")
            return
        await q.message.reply_text("Send the new item name:")
        return

    if data.startswith("buy:"):
        item_id = data.split(":", 1)[1]
        items = _load_items()
        item = next((x for x in items if x["id"] == item_id), None)
        if not item:
            await q.message.reply_text("❌ Item not found.")
            return
        await q.message.reply_text(
            f"🛒 <b>{item['name']}</b>\n"
            f"USDT: <b>{item['price_usdt']}</b>\n"
            f"Stars: <b>{item['price_stars']}</b>\n\n"
            "Choose a payment method:",
            parse_mode=ParseMode.HTML,
            reply_markup=_payment_keyboard(item_id),
        )
        return

    if data.startswith("pay:"):
        _, method, item_id = data.split(":", 2)
        items = _load_items()
        item = next((x for x in items if x["id"] == item_id), None)
        if not item:
            await q.message.reply_text("❌ Item not found.")
            return

        if method == "stars":
            message = (
                f"⭐ Telegram Stars payment\n"
                f"Amount: {item['price_stars']} stars\n"
                "Complete the transfer then click 'I Paid - Verify'."
            )
        else:
            message = (
                f"🟡 Binance payment\n"
                f"Amount: {item['price_usdt']} USDT\n"
                f"Binance Pay ID: {BINANCE_ID}\n"
                "Complete the transfer then click 'I Paid - Verify'."
            )
        await q.message.reply_text(message)
        return

    if data.startswith("verify:"):
        item_id = data.split(":", 1)[1]
        items = _load_items()
        item = next((x for x in items if x["id"] == item_id), None)
        if not item:
            await q.message.reply_text("❌ Item not found.")
            return

        orders = _load_orders()
        order = {
            "item_id": item["id"],
            "item_name": item["name"],
            "buyer_id": q.from_user.id,
            "buyer_username": q.from_user.username,
            "status": "pending_verification",
            "time_utc": datetime.utcnow().isoformat(),
        }
        orders.append(order)
        _save_orders(orders)

        await q.message.reply_text(
            "✅ Your payment verification request has been submitted. "
            "An admin will confirm and deliver your code soon."
        )

        if ADMIN_ID:
            await context.bot.send_message(
                ADMIN_ID,
                f"🧾 Payment verification request\n"
                f"Item: {item['name']}\n"
                f"Buyer: @{q.from_user.username or 'unknown'} ({q.from_user.id})\n"
                f"Open chat and verify payment before sending the code.",
            )
        return


async def admin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Admin only.")
        return ConversationHandler.END
    await update.message.reply_text("➕ Send item name:")
    return ADD_ITEM_NAME


async def admin_add_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_name"] = update.message.text.strip()
    await update.message.reply_text("💰 Send USDT price (example: 12.5):")
    return ADD_ITEM_USDT


async def admin_add_usdt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_usdt"] = float(update.message.text.strip())
    await update.message.reply_text("⭐ Send Telegram Stars price (example: 500):")
    return ADD_ITEM_STARS


async def admin_add_stars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["new_stars"] = int(update.message.text.strip())
    await update.message.reply_text("📝 Send a short description:")
    return ADD_ITEM_DESC


async def admin_add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    items = _load_items()
    name = context.user_data["new_name"]
    usdt = context.user_data["new_usdt"]
    stars = context.user_data["new_stars"]
    desc = update.message.text.strip()
    item_id = name.lower().replace(" ", "-")[:20]
    items.append({"id": item_id, "name": name, "price_usdt": usdt, "price_stars": stars, "description": desc, "emoji": "✨"})
    _save_items(items)
    await update.message.reply_text("✅ Item added successfully.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Canceled.")
    return ConversationHandler.END


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in .env")
    _ensure_files()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))

    conv = ConversationHandler(
        entry_points=[CommandHandler("additem", admin_add_start)],
        states={
            ADD_ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_name)],
            ADD_ITEM_USDT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_usdt)],
            ADD_ITEM_STARS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_stars)],
            ADD_ITEM_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_desc)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
