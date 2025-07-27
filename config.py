#!/usr/bin/env python3
"""
Конфигурация FL.ru RSS Parser
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Telegram настройки (из .env)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# HTTP настройки (из .env с fallback значениями)
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
COOKIES = os.getenv('COOKIES', '')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))

# Форматы дат
DISPLAY_DATE_FORMAT = os.getenv('DISPLAY_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')

# Проверка обязательных переменных
def check_config():
    """Проверяет наличие обязательных настроек"""
    missing = []
    
    if not TELEGRAM_TOKEN:
        missing.append('TELEGRAM_TOKEN')
    
    if not TELEGRAM_CHAT_ID:
        missing.append('TELEGRAM_CHAT_ID')
    
    if missing:
        print("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing:
            print(f"   - {var}")
        print("\nСоздайте файл .env и укажите необходимые значения")
        return False
    
    return True

# Автоматическая проверка при импорте
if __name__ == "__main__":
    check_config()
