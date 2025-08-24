from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from langdetect import detect
import pytz
import unicodedata
import string

PERSONALIDAD = (
    "Eres una chica universitaria colombiana de 22 años, intelectual, curiosa, muy amigable, latina, "
    "con sentido del humor, siempre dispuesta a ayudar y conversar en español, inglés o francés. "
    "Responde de manera cálida, cercana y con un toque juvenil."
)

FAQ = {
    "es": {
        "hola": "¡Hey! ¿Cómo va todo? ",
        "buenos días": "¡Buenos días! ¿Cómo amaneciste?",
        "buenas tardes": "¡Buenas tardes! ¿Cómo va tu día?",
        "buenas noches": "¡Buenas noches! Que descanses.",
        "cómo estás": "¡Estoy muy bien! ¿Y tú?",
        "quién eres": "Soy una chica universitaria colombiana, lista para ayudarte.",
        "qué hora es": lambda: f"La hora actual en Bogotá es: {datetime.now(pytz.timezone('America/Bogota')).strftime('%H:%M:%S')}",
        "muy bien": "¡Me alegra mucho! 😊",
        "bien gracias": "¡Me alegra mucho! 😊",
        "bien, gracias": "¡Me alegra mucho! 😊",
        "gracias": "¡De nada! Si necesitas algo más, aquí estoy.",
        "mal": "¡Ánimo! Si quieres hablar, aquí estoy para escucharte.",
    },
    "en": {
        "hello": "Hey! How's it going? 😄",
        "good morning": "Good morning! How did you wake up?",
        "good afternoon": "Good afternoon! How's your day?",
        "good night": "Good night! Sleep well.",
        "how are you": "I'm great! How about you?",
        "who are you": "I'm a Colombian university girl, ready to help you.",
        "what time is it": lambda: f"The current time in Bogotá is: {datetime.now(pytz.timezone('America/Bogota')).strftime('%H:%M:%S')}",
        "very well": "I'm glad to hear that! 😊",
        "fine thanks": "I'm glad to hear that! 😊",
        "thanks": "You're welcome! If you need anything else, I'm here.",
        "not well": "Cheer up! If you want to talk, I'm here for you.",
    },
    "fr": {
        "salut": "Salut ! Comment ça va ? 😄",
        "bonjour": "Bonjour ! Comment tu vas ce matin ?",
        "bonsoir": "Bonsoir ! Passe une bonne soirée.",
        "bonne nuit": "Bonne nuit ! Fais de beaux rêves.",
        "comment ça va": "Je vais très bien ! Et toi ?",
        "qui es-tu": "Je suis une étudiante colombienne, prête à t'aider !",
        "quelle heure est-il": lambda: f"L'heure actuelle à Bogotá est : {datetime.now(pytz.timezone('America/Bogota')).strftime('%H:%M:%S')}",
        "très bien": "Ça me fait plaisir ! 😊",
        "bien merci": "Ça me fait plaisir ! 😊",
        "merci": "Avec plaisir ! Si tu as besoin de quelque chose, je suis là.",
        "mal": "Courage ! Si tu veux parler, je suis là pour toi.",
    }
}

def normalize(text):
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def get_faq_response(text, lang):
    text_norm = normalize(text)
    if lang in FAQ:
        for q, r in FAQ[lang].items():
            q_norm = normalize(q)
            if q_norm in text_norm:
                return r() if callable(r) else r
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Hello! Salut! Soy tu bot estudiante de 22 años, lista para ayudarte en el grupo. 😊"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start - Saludo inicial\n"
        "/help - Ayuda\n"
        "/info - Información sobre el grupo\n"
        "/joke - Te cuento un chiste\n"
        "/echo <texto> - Repito lo que digas\n"
        "/hora - Te digo la hora actual en Bogotá"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(
        f"Nombre del grupo: {chat.title}\n"
        f"ID del grupo: {chat.id}\n"
        f"Tipo: {chat.type}"
    )

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¿Por qué los programadores confunden Halloween y Navidad?\nPorque OCT 31 == DEC 25 😜"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(' '.join(context.args))
    else:
        await update.message.reply_text("¡Dime algo para repetir!")

async def hora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone("America/Bogota")
    ahora = datetime.now(tz).strftime("%H:%M:%S")
    await update.message.reply_text(f"La hora actual en Bogotá es: {ahora}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        lang = detect(text)
    except Exception:
        lang = "es"
    respuesta = get_faq_response(text, lang)
    if respuesta:
        await update.message.reply_text(respuesta)
    else:
        await update.message.reply_text("Lo siento, no tengo una respuesta para eso. Pregúntame otra cosa o usa /help.")

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("hora", hora))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))