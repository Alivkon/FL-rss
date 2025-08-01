#!/usr/bin/env python3
"""
Setup script для FL.ru RSS Parser
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="fl-rss-parser",
    version="1.0.0",
    author="Ваше имя",
    author_email="your.email@example.com",
    description="Парсер RSS-ленты с сайта FL.ru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fl-rss-parser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fl-rss-parser=get_rss_text:main",
        ],
    },
)
