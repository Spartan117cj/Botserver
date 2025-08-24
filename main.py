import os
import logging
from telegram.ext import ApplicationBuilder
from handlers import setup_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Lee el token desde variable de entorno

def main():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN no está definido en las variables de entorno.")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    setup_handlers(app)
    print("Bot iniciado. Esperando mensajes...")
    app.run_polling()

if __name__ == "__main__":
    main()