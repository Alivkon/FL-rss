#!/usr/bin/env python3
"""
Скрипт настройки .env файла для FL.ru RSS Parser
"""

import os
import shutil

def setup_env():
    """Настройка .env файла"""
    env_example = ".env.example"
    env_file = ".env"
    
    print("🔧 Настройка FL.ru RSS Parser")
    print("=" * 40)
    
    # Проверяем наличие .env.example
    if not os.path.exists(env_example):
        print(f"❌ Файл {env_example} не найден")
        return
    
    # Проверяем, существует ли уже .env
    if os.path.exists(env_file):
        response = input(f"⚠️ Файл {env_file} уже существует. Перезаписать? (y/N): ")
        if response.lower() != 'y':
            print("❌ Настройка отменена")
            return
    
    # Копируем шаблон
    shutil.copy(env_example, env_file)
    print(f"✅ Создан файл {env_file}")
    
    # Интерактивная настройка
    print("\n📝 Настройка переменных окружения:")
    print("(Нажмите Enter для пропуска)")
    
    # Telegram настройки
    print("\n🤖 Telegram настройки:")
    telegram_token = input("TELEGRAM_TOKEN (токен бота): ").strip()
    telegram_chat_id = input("TELEGRAM_CHAT_ID (ID чата): ").strip()
    
    # FL.ru настройки
    print("\n🌐 FL.ru настройки:")
    user_agent = input("USER_AGENT (оставьте пустым для значения по умолчанию): ").strip()
    cookies = input("COOKIES (куки для доступа): ").strip()
    
    # Обновляем .env файл
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if telegram_token:
        content = content.replace('your_bot_token_here', telegram_token)
    
    if telegram_chat_id:
        content = content.replace('your_chat_id_here', telegram_chat_id)
    
    if cookies:
        content = content.replace('your_cookies_here', cookies)
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Файл {env_file} настроен!")
    print("\n📋 Следующие шаги:")
    print("1. Установите зависимости: pip install -r requirements.txt")
    print("2. Протестируйте Telegram бота: python telegram_bot.py")
    print("3. Запустите парсер: python get_rss_text.py")
    
    # Проверяем настройки
    if telegram_token and telegram_chat_id:
        print("\n🧪 Тестирование Telegram бота...")
        test_response = input("Протестировать бота сейчас? (y/N): ")
        if test_response.lower() == 'y':
            os.system("python telegram_bot.py")

if __name__ == "__main__":
    setup_env()