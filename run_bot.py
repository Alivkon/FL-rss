#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота в фоновом режиме
"""

import os
import sys
import signal
import asyncio
from telegram_bot import main as bot_main

def signal_handler(sig, frame):
    """Обработчик сигнала для корректного завершения"""
    print("\nПолучен сигнал завершения. Останавливаем бота...")
    sys.exit(0)

def main():
    """Запуск бота"""
    # Устанавливаем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Запуск Telegram бота для мониторинга FL.ru...")
    print("Для остановки нажмите Ctrl+C")
    
    try:
        # Запускаем бота
        asyncio.run(bot_main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()