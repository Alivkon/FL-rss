# FL.ru RSS Parser

Автоматический парсер RSS-ленты с сайта FL.ru для получения информации о заказах. Сохраняет данные в базу данных SQLite и отправляет уведомления в Telegram.

## 🚀 Быстрый старт

### Установка

```bash
git clone https://github.com/alivkon/FL-rss.git
cd FL-rss
pip install -r requirements.txt
```

### Активация и запуск

1. **Активация виртуального окружения (рекомендуется):**
```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация на Linux/macOS
source venv/bin/activate

# Активация на Windows
venv\Scripts\activate
```

2. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

3. **Настройка конфигурации:**
```bash
cp config.py.example config.py
# Отредактируйте config.py с вашими настройками
```

4. **Запуск парсера:**
```bash
# Запуск с немедленным парсингом + расписание
python get_rss_text.py

# Однократный запуск
python get_rss_text.py --once

# Только по расписанию (без немедленного запуска)
python get_rss_text.py --schedule-only

# Справка
python get_rss_text.py --help
```

## 📋 Режимы работы

### Основной режим (по умолчанию)
```bash
python get_rss_text.py
```
- ✅ Запуск сразу при включении
- ⏰ Затем по расписанию: 9:00, 11:00, 13:00, 15:00, 17:00

### Управление через Telegram бота
```bash
# Запуск бота управления
python parser_manager_bot.py

# Авторизация в боте
/auth FL_RSS_ADMIN_2025
/start
```

### Веб-интерфейс просмотра данных
```bash
# Запуск веб-интерфейса
python viewdatabase.py

# Откройте в браузере: http://localhost:5000
```

## ⚙️ Настройка

### Файл конфигурации `config.py`
```python
# Настройки HTTP-запросов
USER_AGENT = "ваш_user_agent" 
# Пример USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

COOKIES = "ваши_cookies"
#Пример COOKIES = "__ddg1_=pgXi8yXApjYcWufTZrg; _ym_uid=174586895267277; _ym_d=174581446; r2UserId=1745861066098; analytic_id=17458614577462; cookies_accepted=1; mindboxDeviceUUID=ac79e4c3-a0c4-4125-9428-8a3ecdb7; directCrm-session=%7B%22deviceGuid%9e4c3-a0c4-4125-9428-8cdb7%22%7D; _ga_RD9LL0K106=GS1.1.1745861440.1.1.1745863732.42.0.0; _ga=GA1.2.2050675551.1745861441; hidetopprjlenta=0; __ddgid_=4U3z4zXRsVAChIyY; __ddg2_=tzXqvxp86KAib; id=90565; name=profi_pro; pwd=65e4ff2bd982e9cf7fcf6ec9; user_device_id=k35d0g18zx908shntmdcs; _ga_cid_uuid4=00058339-3d20-486a-b505-b78a4978e; PHPSESSID=gKZcV7KBngTeglBQ1yUMabhVyXhm9czwg; new_pf0=1; new_pf10=1; npromo_x=%7B%22close%22%3A1%7D; nomo_open=0; __ddg9_=109.245.36.26; _ym_isad=2; _ym_visorc=w; XSRF-TOKEN=WkIFqBeg6xn5hsoCcl4U8GJanIdp36lIHH; __ddg8_=93RnTius7LBxJv; __ddg10_=175158"

REQUEST_TIMEOUT = 30

# Telegram настройки
TELEGRAM_TOKEN = "ваш_токен_бота"
TELEGRAM_CHAT_ID = "ваш_chat_id"

# Форматы дат
DISPLAY_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
```

### Настройка категорий `included_categories.txt`
```
1    # Программирование
5    # Тексты (автоуведомления)
8    # Дизайн
# 2  # Администрирование (закомментировано)
```

### Ключевые слова `filterList.ini`
```ini
[keywords]
keyword1=python
keyword2=django
keyword3=flask
```

### Стоп-слова `stopwords.ini`
```ini
[stopwords]
stopword1=взлом
stopword2=хакер
stopword3=казино
```

## 🤖 Автозапуск

### Systemd сервис (Linux)
```bash
# Создайте файл сервиса
sudo nano /etc/systemd/system/fl-rss-parser.service
```

```ini
[Unit]
Description=FL.ru RSS Parser Service
After=network.target

[Service]
Type=simple
User=alivkon
Group=alivkon
WorkingDirectory=/home/alivkon/FL-rss
ExecStart=/home/alivkon/FL-rss/venv/bin/python get_rss_text.py
Restart=always
RestartSec=30
Environment=PYTHONPATH=/home/alivkon/projects/FL/FL-rss

[Install]
WantedBy=multi-user.target
```

```bash
# Активация автозапуска
sudo systemctl daemon-reload
sudo systemctl enable fl-rss-parser
sudo systemctl start fl-rss-parser

# Проверка статуса
sudo systemctl status fl-rss-parser
```

### Управляющий скрипт
```bash
# Использование manager.py (если есть)
python manager.py start      # Интерактивный режим
python manager.py daemon     # Фоновый режим
python manager.py stop       # Остановка
python manager.py status     # Статус
```

## 📊 Веб-интерфейс

Доступ к базе данных через браузер:

```bash
python viewdatabase.py
```

Откройте: http://localhost:5000

**Возможности:**
- 📋 Просмотр всех записей (новые сверху)
- 🔍 Поиск по заголовку и описанию
- 📂 Фильтрация по категориям
- 📱 Адаптивный дизайн
- 📈 Статистика в реальном времени

## 📱 Telegram управление

**Команды бота:**
- `/start` - главное меню
- `/status` - статус парсера
- `/logs` - последние логи

**Кнопки управления:**
- ▶️ Запустить - запуск планировщика
- ⏹️ Остановить - остановка парсера
- 🔄 Перезапустить - перезапуск
- 🚀 Запустить один раз - однократный парсинг

## 📁 Структура проекта

```
FL-rss/
├── get_rss_text.py              # 🚀 Основной парсер
├── database.py                  # 🗄️ Работа с БД
├── telegram_bot.py              # 📱 Telegram уведомления
├── parser_manager_bot.py        # 🤖 Бот управления
├── viewdatabase.py              # 🌐 Веб-интерфейс
├── config.py                    # ⚙️ Конфигурация
├── included_categories.txt      # 📂 Настройки категорий
├── filterList.ini               # 🔍 Ключевые слова
├── stopwords.ini                # 🚫 Стоп-слова
├── requirements.txt             # 📦 Зависимости
├── rss_data.db                  # 🗄️ База данных SQLite
└── README.md                    # 📖 Документация
```

## 🔧 Зависимости

```txt
requests>=2.25.1
python-telegram-bot>=20.0
configparser>=5.0.0
schedule>=1.1.0
psutil>=5.8.0
Flask>=2.0.0
```

## 📈 Функции

### ✅ Автоматический парсинг
- Запуск сразу при включении
- Расписание: 9:00, 11:00, 13:00, 15:00, 17:00
- Случайные задержки между запросами

### 📱 Telegram уведомления
- Автоуведомления для категории 5
- Фильтрация по ключевым словам
- Блокировка по стоп-словам

### 🗄️ База данных
- SQLite для надежного хранения
- Дедупликация записей
- Веб-интерфейс для просмотра

### 🤖 Удаленное управление
- Telegram бот для управления
- Systemd интеграция
- Мониторинг процессов

## 🛠️ Решение проблем

### Проблемы с доступом
```bash
# Проверьте cookies и User-Agent в config.py
# Убедитесь в правильности TELEGRAM_TOKEN
```

### Проблемы с базой данных
```bash
# Проверьте права доступа к файлу rss_data.db
# При необходимости удалите и пересоздайте БД
```

### Проблемы с планировщиком
```bash
# Проверьте статус сервиса
sudo systemctl status fl-rss-parser

# Просмотр логов
sudo journalctl -u fl-rss-parser -f
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в терминале
2. Убедитесь в корректности настроек
3. Проверьте доступность FL.ru
4. Используйте `--once` для тестирования

---

**Автор:** alivkon  
**Версия:** 2.0  
**Лицензия:** MIT
