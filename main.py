import os
import json
from dotenv import load_dotenv
from together import Together
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Together initialize
client = Together()

# Diccionario para almacenar los usuarios que ya usaron /start
used_start = {}

# Diccionario para almacenar el historial de cada usuario
user_sessions = {}

# Función que guarda los datos de usuarios en un archivo
def save_data():
    with open("used_start.json", "w") as f:
        json.dump(used_start, f)

# Función para cargar los datos al iniciar el bot
def load_data():
    global used_start
    try:
        with open("used_start.json", "r") as f:
            used_start = json.load(f)
    except FileNotFoundError:
        used_start = {}

# Función limpiar historial
def clear_data():
    global used_start, user_sessions  # Declarar que vas a usar las variables globales

    # Limpiar el diccionario para almacenar los usuarios que ya usaron /start
    used_start.clear()

    # Limpiar el diccionario para almacenar el historial de cada usuario
    user_sessions.clear()

async def cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    clear_data()
     # Enviar la respuesta completa al usuario
    await update.message.reply_text("Data ya fue limpiada.")

# Función para responder al comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    user_id = str(update.effective_user.id)

    if user_id in used_start:
        # Enviar el mensaje de bienvenida
        await update.message.reply_text("Ya has iniciado el bot anteriormente. 😊")
    else:
        # Si el usuario no tiene historial, inicializa uno vacío
        if user_id not in user_sessions:
            user_sessions[user_id] = []
        
        used_start[user_id] = True
        save_data()
        welcome_message = (
            f"👋 ¡Hola {update.effective_user.first_name}! Bienvenido a *Health Partner*.\n\n"
            "Estoy aquí para acompañarte y ayudarte durante todo tu proceso de atención. "
            "Si tienes alguna pregunta o necesitas asistencia, ¡no dudes en pedírmelo!"
        )
        # Agrega el mensaje del usuario al historial de su sesión
        user_sessions[user_id].append({"role": "user", "content": f"Hola, me llamo {update.effective_user.first_name}"})

        # Enviar el mensaje de bienvenida
        await update.message.reply_text(welcome_message, parse_mode="Markdown")  

# Función para responder al comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Puedes usar los siguientes comandos:\n/start - Iniciar el bot\n/help - Obtener ayuda")


# Función para manejar cualquier mensaje de texto y procesarlo con Together API
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Mostrar que el bot está "escribiendo"
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # ID único del usuario
    user_id = str(update.effective_user.id)
    
    # Si el usuario no tiene historial, inicializa uno vacío
    if user_id not in user_sessions:
        user_sessions[user_id] = []

    # Agrega el mensaje del usuario al historial de su sesión
    user_sessions[user_id].append({"role": "user", "content": update.message.text})

    # Inicializa la variable para acumular la respuesta
    text_response = ""

    # Crea la solicitud para Together API, enviando todo el historial de mensajes
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=user_sessions[user_id],  # Envía el historial completo aquí
        stream=True,
    )

    # Procesa el stream y acumula la respuesta
    for chunk in response:
        text_response += chunk.choices[0].delta.content or ""  # Acumula el contenido de cada fragmento
    
    # Agrega la respuesta del modelo al historial del usuario
    user_sessions[user_id].append({"role": "assistant", "content": text_response})

    # Enviar la respuesta completa al usuario
    await update.message.reply_text(text_response)

# Función principal para ejecutar el bot
if __name__ == '__main__':

    # Carga el archivo .env donde tienes almacenado tu token de BotFather
    load_dotenv()

    # Cargar los usuarios al iniciar
    load_data()

    # Asegúrate de que la variable BOT_TOKEN esté en tu archivo .env
    token = os.getenv("BOT_TOKEN")
    
    # Inicializa el bot de Telegram
    app = ApplicationBuilder().token(token).build()

    # Agregar handlers para los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cleanup", cleanup))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot está corriendo...")
    app.run_polling()
