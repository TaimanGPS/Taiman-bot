import os
import requests
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ================= ENV =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "openai/gpt-4o-mini"

# ================= STICKER =================
LOADING_STICKER = "CAACAgIAAxkBAAFHyaNp6GFKMFnsIuNHsh_neEr8XnxxvQACeZwAAoEXQUtx7n3bdzfIXjsE"

# ================= SYSTEM PROMPT =================
system_prompt = """
Sen kuchli AI assistantsan (JARVIS style).
Har doim O‘zbek tilida javob ber.
Aniq, qisqa va tushunarli yoz.
Keraksiz gap qilma.
"""

# ================= AI FUNCTION =================
def get_ai(text):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.6
    }

    try:
        r = requests.post(url, json=data, headers=headers, timeout=30)
        res = r.json()

        if "choices" in res:
            return res["choices"][0]["message"]["content"]
        else:
            return f"❌ API xatolik: {res}"

    except Exception as e:
        return f"❌ Internet/API xatolik: {e}"

# ================= ANIMATION =================
async def animate(update: Update, text: str):
    msg = await update.message.reply_text("✍️ yozilmoqda...")

    out = ""
    for i, w in enumerate(text.split(" ")):
        out += w + " "

        if i % 3 == 0:
            await msg.edit_text(out)
            await asyncio.sleep(0.05)

    await msg.edit_text(out)

# ================= HANDLERS =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    # sticker
    sticker = await update.message.reply_sticker(LOADING_STICKER)

    # AI response
    response = get_ai(update.message.text)

    # remove sticker
    try:
        await sticker.delete()
    except:
        pass

    # animated reply
    await animate(update, response)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Taiman AI tayyor!")

# ================= MAIN =================
def main():

    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN yo‘q (Railway Variables tekshir)")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🤖 Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()