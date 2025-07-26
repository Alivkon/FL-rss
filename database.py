#!/usr/bin/env python3
"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
import os
from datetime import datetime, timedelta
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
    
    def search_by_keywords(self, keywords: List[str], search_in_title: bool = True, search_in_description: bool = True) -> List[Tuple]:
        """Поиск элементов по ключевым словам"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Формируем SQL запрос для поиска
                conditions = []
                params = []
                
                for keyword in keywords:
                    keyword_conditions = []
                    if search_in_title:
                        keyword_conditions.append("LOWER(title) LIKE ?")
                        params.append(f"%{keyword.lower()}%")
                    if search_in_description:
                        keyword_conditions.append("LOWER(description) LIKE ?")
                        params.append(f"%{keyword.lower()}%")
                    
                    if keyword_conditions:
                        conditions.append(f"({' OR '.join(keyword_conditions)})")
                
                if not conditions:
                    return []
                
                query = f'''
                    SELECT DISTINCT id, title, description, link, pub_date, category, created_at
                    FROM rss_items 
                    WHERE {' OR '.join(conditions)}
                    ORDER BY created_at DESC
                '''
                
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            print(f"Ошибка при поиске по ключевым словам: {e}")
            return []

    def create_filtered_database(self, keywords: List[str], output_path: str = None, 
                               search_in_title: bool = True, search_in_description: bool = True) -> str:
        """Создание новой базы данных с проектами, содержащими ключевые слова"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            keywords_str = "_".join(keywords[:3])  # Используем первые 3 ключевых слова для имени
            output_path = f"rss_filtered_{keywords_str}_{timestamp}.db"
        
        try:
            # Создаем новую базу данных
            new_db = RSSDatabase(output_path)
            
            # Получаем отфильтрованные элементы
            filtered_items = self.search_by_keywords(keywords, search_in_title, search_in_description)
            
            if not filtered_items:
                print(f"Не найдено проектов с ключевыми словами: {', '.join(keywords)}")
                return output_path
            
            # Копируем элементы в новую базу
            added_count = 0
            for item in filtered_items:
                id_val, title, description, link, pub_date, category, created_at = item
                
                # Добавляем элемент в новую базу
                success = new_db.add_item(title, description, link, pub_date, category)
                if success:
                    added_count += 1
            
            print(f"✓ Создана база данных с отфильтрованными проектами: {output_path}")
            print(f"✓ Скопировано {added_count} проектов с ключевыми словами: {', '.join(keywords)}")
            
            # Показываем статистику новой базы
            new_stats = new_db.get_statistics()
            print(f"✓ Статистика новой базы: {new_stats.get('total_items', 0)} записей")
            
            return output_path
            
        except Exception as e:
            print(f"Ошибка при создании отфильтрованной базы: {e}")
            return ""

    def get_recent_items(self, days: int = 10) -> List[Tuple]:
        """Получение элементов за последние N дней"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем все элементы для фильтрации
                cursor.execute('''
                    SELECT id, title, description, link, pub_date, category, created_at
                    FROM rss_items 
                    ORDER BY created_at DESC
                ''')
                
                all_items = cursor.fetchall()
                recent_items = []
                cutoff_date = datetime.now() - timedelta(days=days)
                
                for item in all_items:
                    id_val, title, description, link, pub_date, category, created_at = item
                    
                    # Пробуем парсить created_at
                    try:
                        item_date = datetime.fromisoformat(created_at.replace('Z', '+00:00').replace('+00:00', ''))
                    except:
                        # Если не удается распарсить, пропускаем
                        continue
                    
                    # Проверяем, попадает ли дата в диапазон
                    if item_date >= cutoff_date:
                        recent_items.append(item)
                
                return recent_items
                
        except sqlite3.Error as e:
            print(f"Ошибка при получении недавних элементов: {e}")
            return []

    def create_recent_database(self, days: int = 10, output_path: str = None) -> str:
        """Создание новой базы данных с элементами за последние N дней"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"rss_recent_{days}days_{timestamp}.db"
        
        try:
            # Создаем новую базу данных
            new_db = RSSDatabase(output_path)
            
            # Получаем недавние элементы
            recent_items = self.get_recent_items(days)
            
            if not recent_items:
                print(f"Не найдено элементов за последние {days} дней")
                return output_path
            
            # Копируем элементы в новую базу
            added_count = 0
            for item in recent_items:
                id_val, title, description, link, pub_date, category, created_at = item
                
                # Добавляем элемент в новую базу
                success = new_db.add_item(title, description, link, pub_date, category)
                if success:
                    added_count += 1
            
            print(f"✓ Создана база данных с недавними проектами: {output_path}")
            print(f"✓ Скопировано {added_count} проектов за последние {days} дней")
            
            # Показываем статистику новой базы
            new_stats = new_db.get_statistics()
            print(f"✓ Статистика новой базы: {new_stats.get('total_items', 0)} записей")
            
            return output_path
            
        except Exception as e:
            print(f"Ошибка при создании базы недавних проектов: {e}")
            return ""