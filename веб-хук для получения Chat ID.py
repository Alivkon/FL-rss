#!/usr/bin/env python3
"""
Простой способ получения Chat ID через API
"""

import requests
from config import TELEGRAM_TOKEN

def get_updates():
    """Получает обновления через API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['ok'] and data['result']:
            print("Найденные чаты:")
            for update in data['result'][-5:]:
                if 'message' in update:
                    chat = update['message']['chat']
                    user = update['message'].get('from', {})
                    
                    print(f"\nЧат ID: {chat['id']}")
                    print(f"Тип: {chat['type']}")
                    print(f"Пользователь: {user.get('first_name', 'Unknown')}")
                    if 'username' in user:
                        print(f"Username: @{user['username']}")
                    
                    if chat['type'] == 'private':
                        print(f"🔥 Используйте этот Chat ID: {chat['id']}")
        else:
            print("Нет сообщений. Отправьте боту сообщение и запустите заново.")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    print("Поиск Chat ID...")
    get_updates()