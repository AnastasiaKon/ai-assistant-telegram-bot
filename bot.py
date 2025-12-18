import os
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")  # например: https://ai-assiat-bootcamp.onrender.com/ask


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                BACKEND_URL,
                json={"text": user_text},
                timeout=60,
            )

        data = resp.json()

        # 1️⃣ текстовый ответ
        if "answer" in data:
            await update.message.reply_text(data["answer"])

        elif "analysis" in data:
            await update.message.reply_text(data["analysis"])

        elif "error" in data:
            await update.message.reply_text(f"Ошибка 😢\n{data['error']}")

        else:
            await update.message.reply_text("Неожиданный ответ от сервера 🤔")

        # 2️⃣ график (если есть)
        if "chart" in data and data["chart"]:
            try:
                with open(data["chart"], "rb") as f:
                    await update.message.reply_photo(photo=f)
            except Exception:
                await update.message.reply_text("⚠️ Не удалось отправить график")

    except Exception:
        await update.message.reply_text("Ошибка сервера 😢")


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    if not BACKEND_URL:
        raise RuntimeError("BACKEND_URL is not set")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()
