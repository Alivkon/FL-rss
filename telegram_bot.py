#!/usr/bin/env python3
"""
Telegram Bot для уведомлений о новых проектах FL.ru
"""

import configparser
import os
import logging
from typing import Set
import asyncio
from telegram import Bot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Класс для отправки уведомлений в Telegram"""
    
    def __init__(self, token: str, chat_id: str):
        """Инициализация бота"""
        self.bot = Bot(token=token)
        self.chat_id = chat_id
        self.keywords = self.load_keywords()
        self.stopwords = self.load_stopwords()
    
    def load_keywords(self, file_path: str = "filterList.ini") -> Set[str]:
        """Загрузка ключевых слов из файла"""
        keywords = set()
        
        if not os.path.exists(file_path):
            logger.warning(f"Файл {file_path} не найден")
            return keywords
        
        try:
            config = configparser.ConfigParser()
            config.read(file_path, encoding='utf-8')
            
            if 'keywords' in config:
                for key, value in config['keywords'].items():
                    if value.strip():
                        keywords.add(value.strip().lower())
            
            # Если секция [keywords] не найдена, читаем как обычный текстовый файл
            if not keywords:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('['):
                            keywords.add(line.lower())
                            
        except Exception as e:
            logger.error(f"Ошибка при загрузке ключевых слов: {e}")
        
        logger.info(f"Загружено {len(keywords)} ключевых слов")
        return keywords
    
    def load_stopwords(self, file_path: str = "stopwords.ini") -> Set[str]:
        """Загрузка стоп-слов из файла"""
        stopwords = set()
        
        if not os.path.exists(file_path):
            logger.warning(f"Файл стоп-слов {file_path} не найден")
            return stopwords
        
        try:
            config = configparser.ConfigParser()
            config.read(file_path, encoding='utf-8')
            
            if 'stopwords' in config:
                for key, value in config['stopwords'].items():
                    if value.strip():
                        stopwords.add(value.strip().lower())
            
            # Если секция [stopwords] не найдена, читаем как обычный текстовый файл
            if not stopwords:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('['):
                            stopwords.add(line.lower())
                            
        except Exception as e:
            logger.error(f"Ошибка при загрузке стоп-слов: {e}")
        
        logger.info(f"Загружено {len(stopwords)} стоп-слов")
        return stopwords
    
    def check_keywords_in_text(self, text: str) -> bool:
        """Проверка наличия ключевых слов в тексте"""
        if not text or not self.keywords:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)
    
    def check_stopwords_in_text(self, text: str) -> bool:
        """Проверка наличия стоп-слов в тексте"""
        if not text or not self.stopwords:
            return False
        
        text_lower = text.lower()
        found_stopwords = [word for word in self.stopwords if word in text_lower]
        
        if found_stopwords:
            logger.info(f"Найдены стоп-слова: {found_stopwords}")
            return True
        
        return False
    
    def should_notify(self, title: str, description: str, category: int) -> bool:
        """Определяет, нужно ли отправлять уведомление"""
        # Сначала проверяем стоп-слова
        if self.check_stopwords_in_text(title) or self.check_stopwords_in_text(description):
            logger.info(f"Уведомление заблокировано стоп-словами: {title[:50]}")
            return False
        
        # Проверяем категорию 5
        if category == 5:
            return True
        
        # Проверяем ключевые слова в заголовке и описании
        if self.check_keywords_in_text(title) or self.check_keywords_in_text(description):
            return True
        
        return False
    
    def format_message(self, title: str, description: str, link: str, pub_date: str, category: int) -> str:
        """Форматирует сообщение для отправки"""
        # Обрезаем описание до разумной длины
        max_desc_length = 300
        if description and len(description) > max_desc_length:
            description = description[:max_desc_length] + "..."
        
        message = f"🆕 <b>Новый проект FL.ru</b>\n\n"
        message += f"📝 <b>Заголовок:</b> {title}\n\n"
        
        if description:
            message += f"📄 <b>Описание:</b> {description}\n\n"
        
        message += f"🏷 <b>Категория:</b> {category}\n"
        
        if pub_date:
            message += f"📅 <b>Дата публикации:</b> {pub_date}\n"
        
        message += f"🔗 <b>Ссылка:</b> {link}"
        
        return message
    
    async def send_notification(self, title: str, description: str, link: str, pub_date: str, category: int):
        """Отправляет уведомление о проекте"""
        try:
            message = self.format_message(title, description, link, pub_date, category)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
            logger.info(f"Уведомление отправлено: {title[:50]}...")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {e}")
    
    def notify_if_needed(self, title: str, description: str, link: str, pub_date: str, category: int) -> bool:
        """Проверяет и отправляет уведомление если нужно (синхронная версия)"""
        if self.should_notify(title, description, category):
            try:
                # Запускаем асинхронную функцию в новом event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.send_notification(title, description, link, pub_date, category))
                loop.close()
                return True  # Уведомление отправлено
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления: {e}")
                return False
        return False  # Уведомление не требовалось


# Глобальная переменная для хранения экземпляра бота
_telegram_notifier = None

def get_telegram_notifier():
    """Получает экземпляр Telegram уведомителя"""
    global _telegram_notifier
    
    if _telegram_notifier is None:
        try:
            from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
            
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                _telegram_notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
                logger.info("Telegram уведомитель инициализирован")
            else:
                logger.warning("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не настроены")
        except ImportError:
            logger.warning("Не удалось импортировать настройки Telegram")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Telegram бота: {e}")
    
    return _telegram_notifier


def send_telegram_notification(title: str, description: str, link: str, pub_date: str, category: int) -> bool:
    """Отправляет уведомление в Telegram если нужно"""
    notifier = get_telegram_notifier()
    if notifier:
        return notifier.notify_if_needed(title, description, link, pub_date, category)
    return False


async def test_bot():
    """Тестирует работу бота"""
    notifier = get_telegram_notifier()
    if not notifier:
        print("Telegram бот не настроен")
        return False
    
    try:
        await notifier.bot.send_message(
            chat_id=notifier.chat_id,
            text="🤖 Telegram бот FL.ru готов к работе!"
        )
        print("Тестовое сообщение отправлено успешно")
        return True
    except Exception as e:
        print(f"Ошибка при тестировании бота: {e}")
        return False


if __name__ == "__main__":
    # Тестирование бота
    asyncio.run(test_bot())