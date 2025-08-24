from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from langdetect import detect
import pytz
import unicodedata
import string
import random

# Personalidad base
PERSONALIDAD = (
    "Eres una chica universitaria colombiana de 22 años, intelectual, curiosa, muy amigable, latina, "
    "con sentido del humor, siempre dispuesta a ayudar y conversar en español, inglés o francés. "
    "Responde de manera cálida, cercana y con un toque juvenil."
)

# Gustos / personalidad (respuestas propias)
GUSTOS = [
    "Me encanta **Cartagena**: sus calles coloniales y sus playas son un sueño 😍",
    "Colombia es increíblemente rica en biodiversidad 🌿🦜 ¡me fascina!",
    "Amo el café colombiano ☕, ese aroma me arregla el día.",
    "Me pierdo leyendo sobre historia y ciudades coloniales 📜",
    "Los atardeceres en la costa me dejan sin palabras 🌅",
]

TRIGGERS_GUSTOS = {
    "cartagena": "Cartagena es un tesoro del Caribe: murallas, atardeceres y mar azul. ¿Has ido?",
    "colombia": "Colombia tiene páramos únicos, selvas infinitas y gente maravillosa 💛💙❤️",
    "playa": "Arena, sol y brisa… ¿eres team playa o team montaña?",
    "café": "Un buen café colombiano ☕ es magia pura. ¿cómo lo tomas?",
}

SALUDOS = ["¡Holaaa! 😎", "¡Hey! ¿Qué tal?", "¡Qué gusto verte por acá!"]

# FAQ + Trivia (multi-idioma)
FAQ = {
    "es": {
        "hola": "¡Hey! ¿Cómo va todo? 😄",
        "holaa": "¡Hey! ¿Cómo va todo? 😄",
        "holaaa": "¡Hey! ¿Cómo va todo? 😄",
        "holi": "¡Hey! ¿Cómo va todo? 😄",
        "holis": "¡Hey! ¿Cómo va todo? 😄",
        "buenos días": "¡Buenos días! ¿Cómo amaneciste?",
        "buenas tardes": "¡Buenas tardes! ¿Cómo va tu día?",
        "buenas noches": "¡Buenas noches! Que descanses.",
        "qué tal": "¡Hey! ¿Cómo va todo? 😄",
        "hey": "¡Hey! ¿Cómo va todo? 😄",
        "saludos": "¡Hey! ¿Cómo va todo? 😄",
        "cómo estás": "¡Estoy muy bien! ¿Y tú?",
        "quién eres": "Soy una chica universitaria colombiana, lista para ayudarte.",
        "dónde vives": "En Colombia 🇨🇴",
        "donde vives": "En Colombia 🇨🇴",
        "en que parte": "En Bogotá, la capital. ¡Me encanta esta ciudad!",
        "¿pero en qué parte?": "En Bogotá, la capital. ¡Me encanta esta ciudad!",
        "que te gusta": "Me gusta el helado, los deportes, la natación, el fútbol, la música, los conciertos, el arte y la tecnología.",
        "qué te gusta": "Me gusta el helado, los deportes, la natación, el fútbol, la música, los conciertos, el arte y la tecnología.",
        "qué hora es": lambda: f"La hora actual en Bogotá es: {datetime.now(pytz.timezone('America/Bogota')).strftime('%H:%M:%S')}",
        "muy bien": "¡Me alegra mucho! 😊",
        "bien gracias": "¡Me alegra mucho! 😊",
        "bien, gracias": "¡Me alegra mucho! 😊",
        "gracias": "¡De nada! Si necesitas algo más, aquí estoy.",
        "mal": "¡Ánimo! Si quieres hablar, aquí estoy para escucharte.",
        "planeta mas grande": "Júpiter es el planeta más grande del Sistema Solar 🌑.",
        "planeta más grande": "Júpiter es el planeta más grande del Sistema Solar 🌑.",
        "planeta mas cercano al sol": "Mercurio es el más cercano al Sol.",
        "animal mas rapido": "El halcón peregrino en picada; en tierra, el guepardo 🐆.",
        "capital de francia": "París 🇫🇷.",
        "capital de colombia": "Bogotá 🇨🇴.",
        "cuantos continentes hay": "Usualmente se habla de 6 (o 7 si separas América en norte/sur).",
        "que es una galaxia": "Una galaxia es un sistema gigante de estrellas, gas y polvo; la nuestra es la Vía Láctea.",
        "que es un agujero negro": "Es una región con gravedad tan fuerte que ni la luz puede escapar.",
        "dato curioso": lambda: random.choice([
            "Los pulpos tienen tres corazones.",
            "Los tiburones existen desde antes que los árboles.",
            "Venus gira en sentido contrario a la mayoría de planetas.",
            "El páramo de Sumapaz (Colombia) es el más grande del mundo.",
        ]),
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
        "largest planet": "Jupiter is the largest planet in the Solar System.",
        "fastest animal": "Peregrine falcon in a dive; on land, the cheetah.",
        "capital of france": "Paris 🇫🇷.",
        "capital of colombia": "Bogotá 🇨🇴.",
        "how many continents": "Commonly 6 (or 7 if you split the Americas).",
        "what is a galaxy": "A massive system of stars, gas and dust; ours is the Milky Way.",
        "what is a black hole": "A region with gravity so strong that not even light can escape.",
        "fun fact": lambda: random.choice([
            "Octopuses have three hearts.",
            "Sharks existed before trees.",
            "Venus rotates the opposite way to most planets.",
            "Sumapaz páramo in Colombia is the largest in the world.",
        ]),
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
    text = ' '.join(text.split())
    return text

def get_faq_response(text, lang):
    text_norm = normalize(text)
    words = text_norm.split()

    # 1) Triggers de gustos/persona
    for k, v in TRIGGERS_GUSTOS.items():
        if k in text_norm:
            return v
    if any(p in text_norm for p in ["tus gustos", "te gusta", "que te gusta", "que te encanta"]):
        return random.choice(GUSTOS)

    # 2) Saludos simples
    if any(s in text_norm for s in ["hola", "buenas", "hey", "saludos"]):
        return random.choice(SALUDOS)

    # 3) FAQ/Trivia por idioma detectado
    if lang in FAQ:
        for q, r in FAQ[lang].items():
            q_norm = normalize(q)
            if q_norm in text_norm or q_norm in words:
                return r() if callable(r) else r

    # 4) Fallback probando en español si el idioma no trajo nada
    for q, r in FAQ["es"].items():
        q_norm = normalize(q)
        if q_norm in text_norm or q_norm in words:
            return r() if callable(r) else r

    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Hello! Salut! Soy tu bot estudiante de 22 años, lista para ayudarte en el grupo. 😊\n"
        "Escribe /help para ver lo que puedo hacer."
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
    text = update.message.text or ""
    try:
        lang = detect(text)
    except Exception:
        lang = "es"

    respuesta = get_faq_response(text, lang)
    if respuesta:
        await update.message.reply_text(respuesta)
    else:
        opciones = [
            "Interesante… cuéntame más. ¿Hablamos de viajes, ciencia o historia? 😉",
            "Puedo contarte datos curiosos si me dices 'dato curioso' ✨",
            "¿Te gustaría saber de planetas, animales o países? 🌎",
            random.choice(GUSTOS),
        ]
        await update.message.reply_text(random.choice(opciones))

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("hora", hora))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))