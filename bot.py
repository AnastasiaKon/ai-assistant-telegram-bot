import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import httpx
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import Update

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

# ----------------------
# Telegram bot (polling)
# ----------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                BACKEND_URL,
                json={"text": text},
                timeout=60
            )
        data = resp.json()
        answer = data.get("answer") or data.get("error") or "Ошибка 😢"
    except Exception:
        answer = "Ошибка сервера 😢"

    await update.message.reply_text(answer)


def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


# ----------------------
# Dummy HTTP server (for Render)
# ----------------------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


def run_http_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


# ----------------------
# Main
# ----------------------

if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    run_bot()
