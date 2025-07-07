#!/usr/bin/env python3
"""
Простые тесты для FL.ru RSS Parser
"""

import unittest
from unittest.mock import Mock, patch
import requests
import xml.etree.ElementTree as ET

from get_rss_text import get_rss_data, print_and_write
from config import RSS_URL, USER_AGENT, COOKIES


class TestRSSParser(unittest.TestCase):
    """Тесты для RSS парсера"""
    
    @patch('get_rss_text.requests.get')
    def test_get_rss_data_success(self, mock_get):
        """Тест успешного получения данных"""
        # Мокаем успешный ответ
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<?xml version="1.0"?><rss><channel><item><title>Test</title></item></channel></rss>'
        mock_get.return_value = mock_response
        
        result = get_rss_data()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        mock_get.assert_called_once()
    
    @patch('get_rss_text.requests.get')
    def test_get_rss_data_failure(self, mock_get):
        """Тест неудачного получения данных"""
        # Мокаем исключение
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = get_rss_data()
        
        self.assertIsNone(result)
    
    def test_print_and_write(self):
        """Тест функции вывода и записи"""
        from io import StringIO
        
        # Создаем мок файла
        mock_file = StringIO()
        
        with patch('builtins.print') as mock_print:
            print_and_write("Test message", mock_file)
        
        # Проверяем, что print был вызван
        mock_print.assert_called_once_with("Test message")
        
        # Проверяем, что в файл записалось
        mock_file.seek(0)
        content = mock_file.read()
        self.assertEqual(content, "Test message\n")
    
    def test_xml_parsing(self):
        """Тест парсинга XML"""
        xml_content = """<?xml version="1.0"?>
        <rss>
            <channel>
                <item>
                    <title>Test Title</title>
                    <description>Test Description</description>
                    <link>http://example.com</link>
                    <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>"""
        
        root = ET.fromstring(xml_content)
        items = root.findall('.//item')
        
        self.assertEqual(len(items), 1)
        
        item = items[0]
        self.assertEqual(item.find('title').text, "Test Title")
        self.assertEqual(item.find('description').text, "Test Description")
        self.assertEqual(item.find('link').text, "http://example.com")


if __name__ == '__main__':
    unittest.main()
