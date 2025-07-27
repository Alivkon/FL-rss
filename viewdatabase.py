#!/usr/bin/env python3
"""
Веб-интерфейс для просмотра базы данных FL.ru RSS Parser
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import os
from database import RSSDatabase

app = Flask(__name__)

class WebInterface:
    """Класс для веб-интерфейса"""
    
    def __init__(self):
        self.db = RSSDatabase()
    
    def get_items(self, page=1, per_page=50, category=None, search=None):
        """Получает элементы из БД с пагинацией и фильтрацией"""
        offset = (page - 1) * per_page
        
        # Базовый запрос
        query = """
        SELECT id, title, description, link, pub_date, category, created_at 
        FROM rss_items 
        WHERE 1=1
        """
        params = []
        
        # Фильтр по категории
        if category and category != 'all':
            query += " AND category = ?"
            params.append(category)
        
        # Поиск по тексту
        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        
        # Сортировка и пагинация
        query += " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2][:200] + '...' if len(row[2]) > 200 else row[2],
                    'full_description': row[2],
                    'link': row[3],
                    'pub_date': row[4],
                    'category': row[5],
                    'created_at': row[6]
                })
            
            conn.close()
            return items
            
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
    
    def get_total_count(self, category=None, search=None):
        """Получает общее количество записей"""
        query = "SELECT COUNT(*) FROM rss_items WHERE 1=1"
        params = []
        
        if category and category != 'all':
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Ошибка при подсчете записей: {e}")
            return 0
    
    def get_categories(self):
        """Получает список всех категорий"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM rss_items ORDER BY category")
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            return categories
        except Exception as e:
            print(f"Ошибка при получении категорий: {e}")
            return []
    
    def get_statistics(self):
        """Получает статистику БД"""
        stats = self.db.get_statistics()
        
        # Дополнительная статистика
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Статистика по категориям
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM rss_items 
                GROUP BY category 
                ORDER BY count DESC
            """)
            category_stats = dict(cursor.fetchall())
            
            # Статистика по дням
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM rss_items 
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY DATE(created_at) 
                ORDER BY date DESC
            """)
            daily_stats = dict(cursor.fetchall())
            
            conn.close()
            
            stats['category_stats'] = category_stats
            stats['daily_stats'] = daily_stats
            
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
        
        return stats


# Создаем экземпляр веб-интерфейса
web_interface = WebInterface()


@app.route('/')
def index():
    """Главная страница"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    items = web_interface.get_items(page, per_page, category, search)
    total_count = web_interface.get_total_count(category, search)
    categories = web_interface.get_categories()
    statistics = web_interface.get_statistics()
    
    # Пагинация
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('index.html', 
                         items=items,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         total_count=total_count,
                         category=category,
                         search=search,
                         categories=categories,
                         statistics=statistics)


@app.route('/api/item/<int:item_id>')
def get_item(item_id):
    """API для получения полной информации об элементе"""
    try:
        conn = sqlite3.connect(web_interface.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, link, pub_date, category, created_at 
            FROM rss_items 
            WHERE id = ?
        """, (item_id,))
        
        row = cursor.fetchone()
        if row:
            item = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'link': row[3],
                'pub_date': row[4],
                'category': row[5],
                'created_at': row[6]
            }
            conn.close()
            return jsonify(item)
        else:
            conn.close()
            return jsonify({'error': 'Элемент не найден'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """API для получения статистики"""
    stats = web_interface.get_statistics()
    return jsonify(stats)


if __name__ == '__main__':
    # Создаем папку для шаблонов если её нет
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🌐 Запуск веб-интерфейса FL.ru RSS Parser...")
    print("📡 Доступен по адресу: http://localhost:5000")
    print("Для остановки нажмите Ctrl+C")
    
    app.run(host='0.0.0.0', port=5000, debug=True)