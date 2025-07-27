#!/usr/bin/env python3
"""
Telegram Bot для управления FL.ru RSS Parser планировщиком
"""

import asyncio
import logging
import os
import subprocess
import sys
import signal
import psutil
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import schedule
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем настройки из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Глобальные переменные
parser_process = None
scheduler_task = None
authorized_users = set()  # Авторизованные пользователи

# Файлы для управления состоянием
PID_FILE = "parser.pid"
STATUS_FILE = "parser_status.txt"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Я бот для управления FL.ru RSS Parser планировщиком.\n"
                                      "Используйте команды для управления парсером.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status = f.read()
        await update.message.reply_text(f"Текущий статус парсера:\n```\n{status}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text("Парсер не запущен.")

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /logs"""
    if os.path.exists("parser.log"):
        with open("parser.log", "r") as f:
            logs = f.read()
        await update.message.reply_text(f"Логи парсера:\n```\n{logs}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text("Логи отсутствуют.")

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /auth"""
    user_id = update.message.from_user.id
    if user_id not in authorized_users:
        authorized_users.add(user_id)
        await update.message.reply_text("Вы успешно авторизованы для управления парсером.")
    else:
        await update.message.reply_text("Вы уже авторизованы.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_parser":
        await start_parser(query.message, context)
    elif query.data == "stop_parser":
        await stop_parser(query.message, context)
    elif query.data == "restart_parser":
        await restart_parser(query.message, context)
    elif query.data == "view_status":
        await view_status(query.message, context)

async def start_parser(message, context):
    """Запуск парсера"""
    global parser_process
    if parser_process is None or not psutil.pid_exists(parser_process.pid):
        parser_process = subprocess.Popen([sys.executable, "parser_script.py"])
        with open(PID_FILE, "w") as f:
            f.write(str(parser_process.pid))
        await message.reply_text("Парсер запущен.")
    else:
        await message.reply_text("Парсер уже запущен.")

async def stop_parser(message, context):
    """Остановка парсера"""
    global parser_process
    if parser_process is not None and psutil.pid_exists(parser_process.pid):
        os.kill(parser_process.pid, signal.SIGTERM)
        parser_process = None
        os.remove(PID_FILE)
        await message.reply_text("Парсер остановлен.")
    else:
        await message.reply_text("Парсер не запущен.")

async def restart_parser(message, context):
    """Перезапуск парсера"""
    await stop_parser(message, context)
    await start_parser(message, context)

async def view_status(message, context):
    """Просмотр статуса парсера"""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status = f.read()
        await message.reply_text(f"Текущий статус парсера:\n```\n{status}\n```", parse_mode="Markdown")
    else:
        await message.reply_text("Парсер не запущен.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

def main():
    """Основная функция бота"""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не настроен в .env файле")
        print("Создайте .env файл и добавьте:")
        print("TELEGRAM_TOKEN=your_bot_token_here")
        print("TELEGRAM_CHAT_ID=your_chat_id_here")
        return
    
    if not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_CHAT_ID не настроен в .env файле")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("logs", logs_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 FL.ru RSS Parser Manager Bot запущен...")
    print("Для остановки нажмите Ctrl+C")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()