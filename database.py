#!/usr/bin/env python3
"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional


class RSSDatabase:
    """Класс для работы с базой данных RSS заданий"""
    
    def __init__(self, db_path: str = "rss_data.db"):
        """Инициализация базы данных"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Создание таблиц в базе данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rss_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    link TEXT UNIQUE NOT NULL,
                    pub_date TEXT,
                    category INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создаем индексы для оптимизации поиска
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_link ON rss_items(link)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON rss_items(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pub_date ON rss_items(pub_date)')
            
            conn.commit()
    
    def add_item(self, title: str, description: str, link: str, pub_date: str, category: int) -> bool:
        """Добавление нового элемента в базу данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO rss_items 
                    (title, description, link, pub_date, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, description, link, pub_date, category))
                
                # Проверяем, была ли добавлена новая запись
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                return False
                
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении в базу данных: {e}")
            return False
    
    def get_items_by_category(self, category: int) -> List[Tuple]:
        """Получение всех элементов по категории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, description, link, pub_date, category, created_at
                    FROM rss_items 
                    WHERE category = ?
                    ORDER BY pub_date DESC
                ''', (category,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных: {e}")
            return []
    
    def get_all_items(self) -> List[Tuple]:
        """Получение всех элементов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, description, link, pub_date, category, created_at
                    FROM rss_items 
                    ORDER BY pub_date DESC
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """Получение статистики по базе данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество записей
                cursor.execute('SELECT COUNT(*) FROM rss_items')
                total_items = cursor.fetchone()[0]
                
                # Количество записей по категориям
                cursor.execute('''
                    SELECT category, COUNT(*) 
                    FROM rss_items 
                    GROUP BY category 
                    ORDER BY category
                ''')
                by_category = cursor.fetchall()
                
                # Последнее обновление
                cursor.execute('SELECT MAX(created_at) FROM rss_items')
                last_update = cursor.fetchone()[0]
                
                return {
                    'total_items': total_items,
                    'by_category': dict(by_category),
                    'last_update': last_update
                }
        except sqlite3.Error as e:
            print(f"Ошибка при получении статистики: {e}")
            return {}
    
    def clear_category(self, category: int) -> bool:
        """Очистка всех записей определенной категории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM rss_items WHERE category = ?', (category,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при очистке категории: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Очистка всей базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM rss_items')
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при очистке базы данных: {e}")
            return False