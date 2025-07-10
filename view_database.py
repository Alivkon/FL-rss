#!/usr/bin/env python3
"""
Скрипт для просмотра данных из базы данных RSS
"""

import argparse
from database import RSSDatabase
from datetime import datetime


def print_item(item):
    """Выводит информацию об одном элементе"""
    id_val, title, description, link, pub_date, category, created_at = item
    print(f"ID: {id_val}")
    print(f"Категория: {category}")
    print(f"Дата публикации: {pub_date}")
    print(f"Заголовок: {title}")
    print(f"Описание: {description[:200]}{'...' if len(description) > 200 else ''}")
    print(f"Ссылка: {link}")
    print(f"Добавлено в БД: {created_at}")
    print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Просмотр данных из базы RSS")
    parser.add_argument("--category", "-c", type=int, help="Показать элементы только для указанной категории")
    parser.add_argument("--stats", "-s", action="store_true", help="Показать статистику")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Максимальное количество элементов для показа")
    parser.add_argument("--clear", action="store_true", help="Очистить всю базу данных")
    parser.add_argument("--clear-category", type=int, help="Очистить указанную категорию")
    
    args = parser.parse_args()
    
    db = RSSDatabase()
    
    if args.clear:
        confirm = input("Вы действительно хотите очистить всю базу данных? (yes/no): ")
        if confirm.lower() == 'yes':
            if db.clear_all():
                print("База данных очищена")
            else:
                print("Ошибка при очистке базы данных")
        return
    
    if args.clear_category:
        confirm = input(f"Вы действительно хотите очистить категорию {args.clear_category}? (yes/no): ")
        if confirm.lower() == 'yes':
            if db.clear_category(args.clear_category):
                print(f"Категория {args.clear_category} очищена")
            else:
                print("Ошибка при очистке категории")
        return
    
    if args.stats:
        stats = db.get_statistics()
        print("Статистика базы данных:")
        print(f"Всего записей: {stats.get('total_items', 0)}")
        print(f"Последнее обновление: {stats.get('last_update', 'Никогда')}")
        print("\nПо категориям:")
        for category, count in stats.get('by_category', {}).items():
            print(f"  Категория {category}: {count} записей")
        return
    
    # Получаем данные
    if args.category:
        items = db.get_items_by_category(args.category)
        print(f"Элементы для категории {args.category}:")
    else:
        items = db.get_all_items()
        print("Все элементы:")
    
    # Ограничиваем количество
    items = items[:args.limit]
    
    if not items:
        print("Элементы не найдены")
        return
    
    print(f"Показано {len(items)} элементов")
    print("=" * 80)
    
    for item in items:
        print_item(item)


if __name__ == "__main__":
    main()