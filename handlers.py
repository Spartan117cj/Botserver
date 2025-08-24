import os
import openai
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from langdetect import detect
import pytz
import unicodedata
import string

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

PERSONALIDAD = (
    "Eres una chica universitaria colombiana de 22 años, intelectual, curiosa, muy amigable, latina, "
    "con sentido del humor, siempre dispuesta a ayudar y conversar en español, inglés o francés. "
    "Responde de manera cálida, cercana y con un toque juvenil."
)

FAQ = {
    "es": {
        "hola": "¡Hey! ¿Cómo va todo? 😄",
        "buenos días": "¡Buenos días! ¿Cómo amaneciste?",
        "buenas tardes": "¡Buenas tardes! ¿Cómo va tu día?",
        "buenas noches": "¡Buenas noches! Que descanses.",
        "cómo estás": "¡Estoy muy bien! ¿Y tú?",
        "quién eres": "Soy una chica universitaria colombiana, lista para ayudarte.",
        "qué hora es": lambda: f"La hora actual en Bogotá es: {datetime.now(pytz.timezone('America/Bogota')).strftime('%H:%M:%S')}",
    },
    "en": {
        "hello": "Hey! How's it going? 😄",
        "good morning": "Good morning! How did you wake up?",
        "good afternoon": "Good afternoon! How's your day?",
        "good night": "Good night! Sleep well.",
        "how are you": "I'm great! How about you?",
        "who are you": "I'm a Colombian university girl, ready to help you.",
        "what time is it": lambda: f"The current time in Bogotá is: {datetime.now(pytz.timezone('America/Bogota')).strftime('%H:%M:%S')}",
    },
    "fr": {
        "salut": "Salut ! Comment ça va ? 😄",
        "bonjour": "Bonjour ! Comment tu vas ce matin ?",
        "bonsoir": "Bonsoir ! Passe une bonne soirée.",
        "bonne nuit": "Bonne nuit ! Fais de beaux rêves.",
        "comment ça va": "Je vais très bien ! Et toi ?",
        "qui es-tu": "Je suis une étudiante colombienne, prête à t'aider !",
        "quelle heure est-il": lambda: f"L'heure actuelle à Bogotá est : {datetime.now(pytz.timezone('America/Bogota')).strftime('%H:%M:%S')}",
    }
}

def normalize(text):
    # Quita tildes, pasa a minúsculas y elimina signos de puntuación
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
            if normalize(q) in text_norm:
                return r() if callable(r) else r
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Hello! Salut! Soy tu bot estudiante de 22 años, listo para ayudarte en el grupo. 😊"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start - Saludo inicial\n"
        "/help - Ayuda\n"
        "/kick - Expulsar usuario (responde a un mensaje)\n"
        "/info - Información sobre el grupo\n"
        "/joke - Te cuento un chiste\n"
        "/echo <texto> - Repito lo que digas\n"
        "/hora - Te digo la hora actual en Bogotá\n"
        "/pregunta <texto> - Respondo usando IA"
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

async def pregunta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        pregunta_usuario = ' '.join(context.args)
        lang = detect(pregunta_usuario)
        respuesta = get_faq_response(pregunta_usuario, lang)
        if respuesta:
            await update.message.reply_text(respuesta)
        else:
            await update.message.reply_text(
                f"Buscando en internet... (simulado)\nTu pregunta: {pregunta_usuario}\nRespuesta: Lo siento, no tengo acceso real a Google, pero puedo ayudarte con conocimientos generales."
            )
    else:
        await update.message.reply_text("Por favor, escribe una pregunta después del comando /pregunta.")

async def responder_ia(update, context, pregunta_usuario):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": PERSONALIDAD},
                {"role": "user", "content": pregunta_usuario}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        respuesta = response.choices[0].message.content.strip()
        await update.message.reply_text(respuesta)
    except Exception as e:
        # Muestra el error real para depuración
        await update.message.reply_text(f"Lo siento, no pude responder usando IA en este momento. Error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await responder_ia(update, context, text)

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, user_id)
            await update.message.reply_text("Usuario expulsado del grupo. 😎")
        except Exception:
            await update.message.reply_text("No tengo permisos suficientes para expulsar a ese usuario.")
    else:
        await update.message.reply_text("Responde al mensaje del usuario que quieres expulsar usando /kick.")

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("hora", hora))
    app.add_handler(CommandHandler("pregunta", pregunta))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))