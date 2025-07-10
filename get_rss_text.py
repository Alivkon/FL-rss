#!/usr/bin/env python3
"""
FL.ru RSS Parser

Парсер RSS-ленты с сайта FL.ru для получения информации о заказах.
Выводит результаты в консоль, сохраняет в текстовый файл и базу данных SQLite.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os
import time
import random

# Импортируем конфигурацию
from config import (
    USER_AGENT, COOKIES, REQUEST_TIMEOUT,
    OUTPUT_FILE_FORMAT, DATE_FORMAT, DISPLAY_DATE_FORMAT
)

# Импортируем модуль для работы с базой данных
from database import RSSDatabase

# Базовый URL RSS-ленты
RSS_BASE_URL = "https://www.fl.ru/rss/all.xml?category="

# Заголовки для HTTP-запросов
headers = {
    "User-Agent": USER_AGENT,
    "Cookie": COOKIES
}


def get_rss_data(url):
    """Получает данные RSS-ленты"""
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return None


def load_included_categories(file_path="included_categories.txt"):
    """Загружает список категорий для опроса из файла"""
    included = set()
    
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден. Будут опрошены все категории.")
        return set(range(1, 11))  # Все категории по умолчанию
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Пропускаем пустые строки и комментарии
                if line and not line.startswith('#'):
                    try:
                        category = int(line)
                        included.add(category)
                    except ValueError:
                        print(f"Предупреждение: некорректный номер категории '{line}' в файле {file_path}")
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
    
    return included


def print_and_write(text, file_handle):
    """Выводит текст в консоль и записывает в файл"""
    print(text)
    file_handle.write(text + '\n')


def process_rss_item(item, category, file_handle, database):
    """Обрабатывает один элемент RSS и сохраняет его в файл и базу данных"""
    title_elem = item.find('title')
    description_elem = item.find('description')
    link_elem = item.find('link')
    pub_date_elem = item.find('pubDate')
    
    # Извлекаем текст или используем пустую строку
    title = title_elem.text if title_elem is not None else ""
    description = description_elem.text if description_elem is not None else ""
    link = link_elem.text if link_elem is not None else ""
    pub_date = pub_date_elem.text if pub_date_elem is not None else ""
    
    # Выводим и записываем в файл
    if pub_date:
        print_and_write(f"Дата публикации: {pub_date}", file_handle)
    if title:
        print_and_write(f"Заголовок: {title}", file_handle)
    if description:
        print_and_write(f"Описание: {description}", file_handle)
    if link:
        print_and_write(f"Ссылка: {link}", file_handle)
    print_and_write('-' * 40, file_handle)
    
    # Сохраняем в базу данных
    if link:  # Ссылка обязательна для сохранения
        success = database.add_item(title, description, link, pub_date, category)
        if success:
            print(f"✓ Сохранено в БД: {title[:50]}{'...' if len(title) > 50 else ''}")
        else:
            print(f"⚠ Уже существует в БД: {title[:50]}{'...' if len(title) > 50 else ''}")


def main():
    """Основная функция программы"""
    # Инициализируем базу данных
    db = RSSDatabase()
    
    # Создаем папку для текстов если её нет
    if not os.path.exists('texts'):
        os.makedirs('texts')
    
    # Загружаем включённые категории
    included_categories = load_included_categories()
    
    # Показываем информацию о включённых категориях
    if included_categories:
        print(f"Включённые категории: {sorted(included_categories)}")
    else:
        print("Включённые категории не найдены. Будут опрошены все категории.")
        included_categories = set(range(1, 11))  # Все категории по умолчанию
    
    # Показываем статистику базы данных
    stats = db.get_statistics()
    if stats:
        print(f"\nСтатистика базы данных:")
        print(f"Всего записей: {stats.get('total_items', 0)}")
        print(f"Последнее обновление: {stats.get('last_update', 'Никогда')}")
    
    total_new_items = 0
    
    # Выполняем запросы для выбранных категорий
    for category in sorted(included_categories):
        # Проверяем, что категория в допустимом диапазоне
        if category <= 0 or category > 50:           # Здесь задаём категории
            print(f"Предупреждение: категория {category} вне допустимого диапазона (1-10)")
            continue
        
        print(f"\nОбработка категории {category}...")
        
        # Формируем URL для текущей категории
        url = f"{RSS_BASE_URL}{category}"
        
        # Получаем данные RSS-ленты
        response = get_rss_data(url)
        
        if response is None:
            print(f"Не удалось получить данные для категории {category}")
            continue
        
        print(f"HTTP статус: {response.status_code}")
        
        # Создаем файл для записи результатов
        output_file = f"texts/rss_category_{category}_{datetime.now().strftime(DATE_FORMAT)}.txt"
        
        if response.status_code == 200:
            with open(output_file, 'w', encoding='utf-8') as f:
                print_and_write(f"Результаты парсинга RSS для категории {category} от {datetime.now().strftime(DISPLAY_DATE_FORMAT)}", f)
                print_and_write("=" * 60, f)
                print_and_write(f"URL: {url}", f)
                print_and_write("", f)
                
                try:
                    root = ET.fromstring(response.content)
                    items_count = 0
                    new_items_count = 0
                    
                    for item in root.findall('.//item'):
                        # Обрабатываем элемент
                        old_total = db.get_statistics().get('total_items', 0)
                        process_rss_item(item, category, f, db)
                        new_total = db.get_statistics().get('total_items', 0)
                        
                        if new_total > old_total:
                            new_items_count += 1
                        
                        items_count += 1
                    
                    print_and_write("", f)
                    print_and_write(f"Обработано элементов: {items_count}", f)
                    print_and_write(f"Новых элементов в БД: {new_items_count}", f)
                    print_and_write(f"Результаты сохранены в файл: {output_file}", f)
                    
                    total_new_items += new_items_count
                    print(f"Категория {category}: обработано {items_count} элементов, новых в БД: {new_items_count}")
                    
                except ET.ParseError as e:
                    error_msg = f"Ошибка парсинга XML: {e}"
                    print_and_write(error_msg, f)
                    
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                error_msg = f"Ошибка доступа (HTTP {response.status_code}). Возможно, требуется авторизация или сайт блокирует ботов."
                print_and_write(error_msg, f)
        
        # Добавляем задержку между запросами (от 1 до 3 секунд)
        if category != max(included_categories):  # Не делаем задержку после последнего запроса
            delay = random.uniform(5, 25) 
            print(f"Ожидание {delay:.2f} секунд перед следующим запросом...")
            time.sleep(delay)
    
    # Показываем финальную статистику
    final_stats = db.get_statistics()
    print(f"\n{'='*60}")
    print("Все запросы завершены!")
    print(f"Результаты сохранены в папку 'texts'")
    print(f"Всего новых записей добавлено в БД: {total_new_items}")
    print(f"Общее количество записей в БД: {final_stats.get('total_items', 0)}")
    print(f"База данных: {db.db_path}")


if __name__ == "__main__":
    main()