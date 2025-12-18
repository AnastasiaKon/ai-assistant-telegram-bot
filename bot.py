import os
import httpx
from fastapi import FastAPI, Request

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")  # https://<backend>.onrender.com/ask
PUBLIC_URL = os.getenv("PUBLIC_URL")    # https://<bot-service>.onrender.com
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET", "secret")

app = FastAPI()


@app.on_event("startup")
async def set_webhook():
    # Регистрируем webhook в Telegram
    webhook_url = f"{PUBLIC_URL}/telegram/webhook"
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
            json={
                "url": webhook_url,
                "secret_token": SECRET_TOKEN,
                "drop_pending_updates": True,
            },
            timeout=30,
        )


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()

    message = update.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # ПРОСТОЙ ТЕСТОВЫЙ ОТВЕТ
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": f"Эхо: {text}"
            },
            timeout=30
        )

    return {"ok": True}



@app.get("/health")
def health():
    return {"status": "ok"}
