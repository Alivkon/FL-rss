#!/usr/bin/env python3
"""
FL.ru RSS Parser

Парсер RSS-ленты с сайта FL.ru для получения информации о заказах.
Сохраняет в базу данных SQLite и отправляет уведомления в Telegram.

Расписание: запуск сразу при включении, затем в 9:00, 11:00, 13:00, 15:00, 17:00 ежедневно
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, time
import sys
import os
import time as time_module
import random
import schedule
import signal

# Импортируем конфигурацию
from config import (
    USER_AGENT, COOKIES, REQUEST_TIMEOUT,
    DISPLAY_DATE_FORMAT
)

# Импортируем модуль для работы с базой данных
from database import RSSDatabase

# Импортируем Telegram уведомления
from telegram_bot import send_telegram_notification

# Базовый URL RSS-ленты
RSS_BASE_URL = "https://www.fl.ru/rss/all.xml?category="

# Заголовки для HTTP-запросов
headers = {
    "User-Agent": USER_AGENT,
    "Cookie": COOKIES
}

# Флаг для остановки планировщика
running = True


def signal_handler(signum, frame):
    """Обработчик сигнала для корректного завершения"""
    global running
    print("\nПолучен сигнал завершения. Останавливаем планировщик...")
    running = False


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


def process_rss_item(item, category, database):
    """Обрабатывает один элемент RSS и сохраняет его в базу данных"""
    title_elem = item.find('title')
    description_elem = item.find('description')
    link_elem = item.find('link')
    pub_date_elem = item.find('pubDate')
    
    # Извлекаем текст или используем пустую строку
    title = title_elem.text if title_elem is not None else ""
    description = description_elem.text if description_elem is not None else ""
    link = link_elem.text if link_elem is not None else ""
    pub_date = pub_date_elem.text if pub_date_elem is not None else ""
    
    # Выводим информацию в консоль
    print(f"Заголовок: {title}")
    if description:
        print(f"Описание: {description[:100]}{'...' if len(description) > 100 else ''}")
    print(f"Ссылка: {link}")
    if pub_date:
        print(f"Дата: {pub_date}")
    print('-' * 40)
    
    telegram_sent = False  # Флаг отправки в Telegram
    
    # Сохраняем в базу данных
    if link:  # Ссылка обязательна для сохранения
        success = database.add_item(title, description, link, pub_date, category)
        if success:
            print(f"✓ Сохранено в БД: {title[:50]}{'...' if len(title) > 50 else ''}")
            
            # Отправляем Telegram уведомление для новых записей
            try:
                telegram_sent = send_telegram_notification(title, description, link, pub_date, category)
                if telegram_sent:
                    print(f"📱 Уведомление отправлено в Telegram")
                else:
                    # Проверяем, было ли заблокировано стоп-словами
                    from telegram_bot import get_telegram_notifier
                    notifier = get_telegram_notifier()
                    if notifier and (notifier.check_stopwords_in_text(title) or notifier.check_stopwords_in_text(description)):
                        print(f"🚫 Уведомление заблокировано стоп-словами")
            except Exception as e:
                print(f"Ошибка при отправке Telegram уведомления: {e}")
                
        else:
            print(f"⚠ Уже существует в БД: {title[:50]}{'...' if len(title) > 50 else ''}")
    
    return telegram_sent


def parse_rss():
    """Основная функция парсинга RSS"""
    print(f"\n{'='*80}")
    print(f"🚀 ЗАПУСК ПАРСЕРА FL.ru - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Инициализируем базу данных
    db = RSSDatabase()
    
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
    total_telegram_sent = 0  # Счетчик отправленных в Telegram
    
    # Выполняем запросы для выбранных категорий
    for category in sorted(included_categories):
        # Проверяем, что категория в допустимом диапазоне
        if category < 0 or category > 42:
            print(f"Предупреждение: категория {category} вне допустимого диапазона (1-42)")
            continue
        
        print(f"\n{'='*60}")
        print(f"Обработка категории {category} - {datetime.now().strftime(DISPLAY_DATE_FORMAT)}")
        print(f"URL: {RSS_BASE_URL}{category}")
        print('='*60)
        
        # Получаем данные RSS-ленты
        response = get_rss_data(f"{RSS_BASE_URL}{category}")
        
        if response is None:
            print(f"Не удалось получить данные для категории {category}")
            continue
        
        print(f"HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                items_count = 0
                new_items_count = 0
                telegram_sent_count = 0  # Счетчик для текущей категории
                
                for item in root.findall('.//item'):
                    # Обрабатываем элемент
                    old_total = db.get_statistics().get('total_items', 0)
                    telegram_sent = process_rss_item(item, category, db)
                    new_total = db.get_statistics().get('total_items', 0)
                    
                    if new_total > old_total:
                        new_items_count += 1
                    
                    if telegram_sent:
                        telegram_sent_count += 1
                    
                    items_count += 1
                
                print(f"\n{'='*40}")
                print(f"Обработано элементов: {items_count}")
                print(f"Новых элементов в БД: {new_items_count}")
                print(f"Отправлено в Telegram: {telegram_sent_count}")
                print(f"{'='*40}")
                
                total_new_items += new_items_count
                total_telegram_sent += telegram_sent_count
                print(f"Категория {category}: обработано {items_count} элементов, новых в БД: {new_items_count}, отправлено в Telegram: {telegram_sent_count}")
                
            except ET.ParseError as e:
                error_msg = f"Ошибка парсинга XML: {e}"
                print(error_msg)
                
        else:
            error_msg = f"Ошибка доступа (HTTP {response.status_code}). Возможно, требуется авторизация или сайт блокирует ботов."
            print(error_msg)
        
        # Добавляем задержку между запросами (от 60 до 360 секунд)
        if category != max(included_categories):  # Не делаем задержку после последнего запроса
            delay = random.uniform(60, 360) 
            print(f"Ожидание {delay:.2f} секунд перед следующим запросом...")
            time_module.sleep(delay)
    
    # Показываем финальную статистику
    final_stats = db.get_statistics()
    print(f"\n{'='*60}")
    print("✅ ПАРСИНГ ЗАВЕРШЕН!")
    print(f"Всего новых записей добавлено в БД: {total_new_items}")
    print(f"Всего отправлено в Telegram: {total_telegram_sent}")
    print(f"Общее количество записей в БД: {final_stats.get('total_items', 0)}")
    print(f"База данных: {db.db_path}")
    
    # Показываем следующий запуск только если планировщик работает
    next_run = schedule.next_run()
    if next_run:
        print(f"Следующий запуск: {next_run}")
    
    print(f"{'='*60}")


def setup_schedule():
    """Настройка расписания запуска парсера"""
    # Расписание: 9:00, 11:00, 13:00, 15:00, 17:00
    schedule.every().day.at("09:00").do(parse_rss)
    schedule.every().day.at("11:00").do(parse_rss)
    schedule.every().day.at("13:00").do(parse_rss)
    schedule.every().day.at("15:00").do(parse_rss)
    schedule.every().day.at("17:00").do(parse_rss)
    
    print("\n📅 Расписание настроено:")
    print("   - 09:00 (утренний запуск)")
    print("   - 11:00 (через 2 часа)")
    print("   - 13:00 (через 2 часа)")
    print("   - 15:00 (через 2 часа)")
    print("   - 17:00 (вечерний запуск)")
    
    next_run = schedule.next_run()
    if next_run:
        print(f"Следующий запуск: {next_run}")
    else:
        print("Следующий запуск: завтра в 09:00")


def run_scheduler():
    """Запуск планировщика с немедленным первым запуском"""
    global running
    
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"\n🤖 FL.ru RSS Parser запущен - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Режим: автоматический запуск при включении + расписание")
    print("Для остановки нажмите Ctrl+C")
    
    # НЕМЕДЛЕННЫЙ ЗАПУСК при включении (в любое время)
    print("\n🚀 НЕМЕДЛЕННЫЙ ЗАПУСК ПАРСЕРА...")
    parse_rss()
    
    # Настраиваем расписание после первого запуска
    setup_schedule()
    
    # Основной цикл планировщика
    print(f"\n⏰ Переход в режим ожидания расписания...")
    while running:
        try:
            schedule.run_pending()
            time_module.sleep(60)  # Проверяем каждую минуту
        except KeyboardInterrupt:
            running = False
            break
        except Exception as e:
            print(f"Ошибка в планировщике: {e}")
            time_module.sleep(60)
    
    print("\n👋 Планировщик остановлен")


def run_scheduler_no_immediate():
    """Запуск планировщика только по расписанию (без немедленного запуска)"""
    global running
    
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Настраиваем расписание
    setup_schedule()
    
    print(f"\n🤖 FL.ru RSS Parser запущен - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Режим: только по расписанию")
    print("Для остановки нажмите Ctrl+C")
    
    # Проверяем, нужно ли запустить в рабочее время
    current_time = datetime.now().time()
    work_start = time(9, 0)
    work_end = time(17, 30)
    
    if work_start <= current_time <= work_end:
        print("\n⏰ Рабочее время! Запускаем парсер...")
        parse_rss()
    else:
        print(f"\n💤 Не рабочее время ({current_time.strftime('%H:%M')}). Ожидание расписания...")
    
    # Основной цикл планировщика
    while running:
        try:
            schedule.run_pending()
            time_module.sleep(60)  # Проверяем каждую минуту
        except KeyboardInterrupt:
            running = False
            break
        except Exception as e:
            print(f"Ошибка в планировщике: {e}")
            time_module.sleep(60)
    
    print("\n👋 Планировщик остановлен")


def main():
    """Главная функция - выбор режима работы"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            # Однократный запуск
            print("🔄 Режим однократного запуска")
            parse_rss()
        elif sys.argv[1] == "--schedule-only":
            # Только по расписанию (без немедленного запуска)
            print("⏰ Режим планировщика (только по расписанию)")
            run_scheduler_no_immediate()
        elif sys.argv[1] == "--help":
            print_help()
        else:
            print(f"❌ Неизвестный параметр: {sys.argv[1]}")
            print_help()
    else:
        # Режим по умолчанию: немедленный запуск + планировщик
        print("🚀 Режим автоматического запуска")
        run_scheduler()


def print_help():
    """Показать справку по использованию"""
    print("""
FL.ru RSS Parser - Справка по использованию

Режимы запуска:
    python get_rss_text.py              - Запуск сразу + по расписанию (по умолчанию)
    python get_rss_text.py --once       - Однократный запуск
    python get_rss_text.py --schedule-only  - Только по расписанию без немедленного запуска
    python get_rss_text.py --help       - Эта справка

Режим по умолчанию:
    - Парсер запускается СРАЗУ при включении (в любое время)
    - Затем работает по расписанию: 9:00, 11:00, 13:00, 15:00, 17:00

Расписание:
    09:00 - утренний запуск
    11:00 - через 2 часа
    13:00 - через 2 часа
    15:00 - через 2 часа
    17:00 - вечерний запуск

Для остановки используйте Ctrl+C
    """)


if __name__ == "__main__":
    main()