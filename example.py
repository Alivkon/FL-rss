#!/usr/bin/env python3
"""
Пример использования FL.ru RSS Parser

Демонстрирует как использовать модуль для получения данных RSS.
"""

from get_rss_text import get_rss_data, print_and_write
from datetime import datetime

if __name__ == "__main__":
    print("=== Пример использования FL.ru RSS Parser ===\n")
    
    # Получаем данные
    response = get_rss_data()
    
    if response and response.status_code == 200:
        print("Успешно получены данные RSS-ленты!")
        print(f"Размер ответа: {len(response.content)} байт")
        
        # Показываем первые 200 символов
        print("\nПервые 200 символов:")
        print(response.text[:200])
        
    else:
        print("Не удалось получить данные RSS-ленты")
        if response:
            print(f"HTTP код: {response.status_code}")
