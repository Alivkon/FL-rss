# Makefile для FL.ru RSS Parser

.PHONY: help install run test clean

help:
	@echo "Доступные команды:"
	@echo "  install  - Установить зависимости"
	@echo "  run      - Запустить парсер"
	@echo "  test     - Запустить тесты"
	@echo "  clean    - Очистить временные файлы"
	@echo "  help     - Показать это сообщение"

install:
	pip install -r requirements.txt

run:
	python3 get_rss_text.py

test:
	python3 -m unittest test_rss_parser.py -v

clean:
	rm -f rss_output_*.txt
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache
