# RSS Parser для FL.ru

Простой парсер RSS-ленты с сайта FL.ru (Freelance.ru) для категории "Программирование".

## Описание

Программа получает RSS-ленту с сайта FL.ru, парсит её и выводит информацию о заказах в консоль и текстовый файл. Для каждого заказа выводится:
- Дата публикации
- Заголовок
- Описание
- Ссылка на заказ

## Требования

- Python 3.6+
- requests
- xml.etree.ElementTree (встроенный модуль)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/fl-rss-parser.git
cd fl-rss-parser
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

Запустите скрипт:
```bash
python get_rss_text.py
```

Программа создаст файл с результатами в формате `rss_output_YYYYMMDD_HHMMSS.txt`.

## Структура проекта

```
fl-rss-parser/
├── get_rss_text.py      # Основной скрипт
├── requirements.txt     # Зависимости
├── README.md           # Документация
├── .gitignore          # Игнорируемые файлы
└── LICENSE             # Лицензия
```

## Примечания

- Программа использует cookies для авторизации на сайте FL.ru
- Обновите cookies в коде, если они устарели
- Результаты сохраняются в файлы с временными метками

## Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## Автор

Ваше имя
