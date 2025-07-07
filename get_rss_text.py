#!/usr/bin/env python3
"""
FL.ru RSS Parser

Парсер RSS-ленты с сайта FL.ru для получения информации о заказах.
Выводит результаты в консоль и сохраняет в текстовый файл.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os

# Импортируем конфигурацию
from config import (
    RSS_URL, USER_AGENT, COOKIES, REQUEST_TIMEOUT,
    OUTPUT_FILE_FORMAT, DATE_FORMAT, DISPLAY_DATE_FORMAT
)

# Заголовки для HTTP-запросов
headers = {
    "User-Agent": USER_AGENT,
    "Cookie": COOKIES
}


def get_rss_data():
    """Получает данные RSS-ленты"""
    try:
        response = requests.get(RSS_URL, headers=headers, timeout=REQUEST_TIMEOUT)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return None

def print_and_write(text, file_handle):
    """Выводит текст в консоль и записывает в файл"""
    print(text)
    file_handle.write(text + '\n')


def main():
    """Основная функция программы"""
    # Создаем файл для записи результатов
    output_file = f"rss_output_{datetime.now().strftime(DATE_FORMAT)}.txt"
    
    print("Получение данных RSS-ленты...")
    response = get_rss_data()
    
    if response is None:
        print("Не удалось получить данные RSS-ленты")
        return
    
    print(f"HTTP статус: {response.status_code}")
    print("Первые 200 символов ответа:")
    print(response.text[:400])

    if response.status_code == 200:
        with open(output_file, 'w', encoding='utf-8') as f:
            print_and_write(f"Результаты парсинга RSS от {datetime.now().strftime(DISPLAY_DATE_FORMAT)}", f)
            print_and_write("=" * 60, f)
            print_and_write("", f)
            
            try:
                root = ET.fromstring(response.content)
                items_count = 0
                
                for item in root.findall('.//item'):
                    title = item.find('title')
                    description = item.find('description')
                    link = item.find('link')
                    pubDate = item.find('pubDate')
                    
                    if pubDate is not None:
                        print_and_write(f"Дата публикации: {pubDate.text}", f)
                    if title is not None:
                        print_and_write(f"Заголовок: {title.text}", f)
                    if description is not None:
                        print_and_write(f"Описание: {description.text}", f)
                    if link is not None:
                        print_and_write(f"Ссылка: {link.text}", f)
                    print_and_write('-' * 40, f)
                    items_count += 1
                
                print_and_write("", f)
                print_and_write(f"Обработано элементов: {items_count}", f)
                print_and_write(f"Результаты сохранены в файл: {output_file}", f)
                
            except ET.ParseError as e:
                error_msg = f"Ошибка парсинга XML: {e}"
                print_and_write(error_msg, f)
                
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            error_msg = f"Ошибка доступа (HTTP {response.status_code}). Возможно, требуется авторизация или сайт блокирует ботов."
            print_and_write(error_msg, f)


if __name__ == "__main__":
    main()