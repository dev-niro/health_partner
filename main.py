import os
import json
import requests
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI

# Función para responder al comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hola {update.effective_user.first_name}, ¡bienvenido al bot!")

# Función para responder al comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Puedes usar los siguientes comandos:\n/start - Iniciar el bot\n/help - Obtener ayuda")

# Función para responder a cualquier mensaje de texto
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    base_url = "https://api.aimlapi.com/v1"
    api_key = "8752382bffb4404296f3b4dfa20ac5f9"
    system_prompt = "You are a travel agent. Be descriptive and helpful."
    user_prompt = "Tell me about San Francisco"

    api = OpenAI(api_key=api_key, base_url=base_url)
    completion = api.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=256,
    )

    response = completion.choices[0].message.content

    print("User:", user_prompt)
    print("AI:", response)
    await update.message.reply_text(response)

# Función principal para ejecutar el bot
if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN")  # Reemplaza con tu token de BotFather
    app = ApplicationBuilder().token(token).build()

    # Agregar handlers para los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot está corriendo...")
    app.run_polling()
