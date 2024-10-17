import os
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from together import Together

# Función para responder al comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hola {update.effective_user.first_name}, ¡bienvenido al bot!")

# Función para responder al comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Puedes usar los siguientes comandos:\n/start - Iniciar el bot\n/help - Obtener ayuda")

# Función para manejar cualquier mensaje de texto y procesarlo con Together API
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    client = Together()

    # Inicializa la variable para acumular la respuesta
    text_response = ""

    # Crea la solicitud para Together API
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": update.message.text}],
        stream=True,
    )

    # Procesa el stream y acumula la respuesta
    for chunk in response:
        text_response += chunk.choices[0].delta.content or ""  # Acumula el contenido de cada fragmento
    
    # Enviar la respuesta completa al usuario
    await update.message.reply_text(text_response)

# Función principal para ejecutar el bot
if __name__ == '__main__':
    # Carga el archivo .env donde tienes almacenado tu token de BotFather
    load_dotenv()
    token = os.getenv("BOT_TOKEN")  # Asegúrate de que la variable BOT_TOKEN esté en tu archivo .env
    
    # Inicializa el bot de Telegram
    app = ApplicationBuilder().token(token).build()

    # Agregar handlers para los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot está corriendo...")
    app.run_polling()
