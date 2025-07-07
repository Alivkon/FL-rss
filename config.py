"""
Конфигурация для FL.ru RSS Parser
"""

# URL RSS-ленты
RSS_URL = "https://www.fl.ru/rss/all.xml?category=2"

# User-Agent для HTTP-запросов
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Cookies для авторизации (обновите при необходимости)
# Получите актуальные cookies из браузера после авторизации на FL.ru
COOKIES = "__ddg1_=pgXi8yXApjrYcWufTZrg; _ym_uid=1745861446895267277; _ym_d=1745861446; r2UserId=1745861452066098; analytic_id=1745861452077462; cookies_accepted=1; mindboxDeviceUUID=ac79e4c3-a0c4-4125-9428-8a33529ecdb7; directCrm-session=%7B%22deviceGuid%22%3A%22ac79e4c3-a0c4-4125-9428-8a33529ecdb7%22%7D; _ga_RD9LL0K106=GS1.1.1745861440.1.1.1745863732.42.0.0; _ga=GA1.2.2050675551.1745861441; hidetopprjlenta=0; __ddgid_=4U3z4zXRsVAChIyY; __ddg2_=tzXqvxp82ii6KAib; id=9052465; name=profi_prog; pwd=65e4ff2bd982e606f528d9cf7fcf6ec9; user_device_id=k35d07ouvg18zx4daggqe908shntmdcs; _ga_cid_uuid4=00058339-3d20-486a-b505-b78a4ab6978e; PHPSESSID=gKZcV7KBngTeg6LyRZG9lBQ1yUMabhVyXhm9czwg; new_pf0=1; new_pf10=1; nfastpromo_x=%7B%22close%22%3A1%7D; nfastpromo_open=0; __ddg9_=109.245.36.26; _ym_isad=2; _ym_visorc=w; XSRF-TOKEN=WkIFqBeg6LHv8s7xn5hsoCcl4U8GJanIdp36lIHH; __ddg8_=93RnTiuxPs7LBxJv; __ddg10_=1750703158"

# Таймаут для HTTP-запросов (в секундах)
REQUEST_TIMEOUT = 10

# Формат файла вывода
OUTPUT_FILE_FORMAT = "rss_output_{timestamp}.txt"
DATE_FORMAT = "%Y%m%d_%H%M%S"
DISPLAY_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
