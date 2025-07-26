# FL.ru RSS Parser

Парсер RSS-ленты с сайта FL.ru для получения информации о заказах. Сохраняет данные в текстовые файлы и базу данных SQLite.

## Установка

```bash
git clone https://github.com/yourusername/FL-rss.git
cd FL-rss
pip install -r requirements.txt
```

## Использование

```bash
python get_rss_text.py
```

## Настройка категорий

Отредактируйте файл `included_categories.txt`, раскомментировав нужные категории:

```
1
# 2
5
```

## Результаты

- Текстовые файлы: папка `texts/`
- База данных: `rss_data.db`

## Структура проекта

```
FL-rss/
├── get_rss_text.py          # Основной скрипт
├── database.py              # Модуль работы с БД
├── config.py                # Конфигурация
├── included_categories.txt  # Настройки категорий
├── requirements.txt         # Зависимости
└── README.md               # Документация
```
