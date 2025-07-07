import requests
import xml.etree.ElementTree as ET
from datetime import datetime

url = "https://www.fl.ru/rss/all.xml?category=2"

headers = {
    "User-Agent": "...",
    "Cookie": "__ddg1_=pgXi8yXApjrYcWufTZrg; _ym_uid=1745861446895267277; _ym_d=1745861446; r2UserId=1745861452066098; analytic_id=1745861452077462; cookies_accepted=1; mindboxDeviceUUID=ac79e4c3-a0c4-4125-9428-8a33529ecdb7; directCrm-session=%7B%22deviceGuid%22%3A%22ac79e4c3-a0c4-4125-9428-8a33529ecdb7%22%7D; _ga_RD9LL0K106=GS1.1.1745861440.1.1.1745863732.42.0.0; _ga=GA1.2.2050675551.1745861441; hidetopprjlenta=0; __ddgid_=4U3z4zXRsVAChIyY; __ddg2_=tzXqvxp82ii6KAib; id=9052465; name=profi_prog; pwd=65e4ff2bd982e606f528d9cf7fcf6ec9; user_device_id=k35d07ouvg18zx4daggqe908shntmdcs; _ga_cid_uuid4=00058339-3d20-486a-b505-b78a4ab6978e; PHPSESSID=gKZcV7KBngTeg6LyRZG9lBQ1yUMabhVyXhm9czwg; new_pf0=1; new_pf10=1; nfastpromo_x=%7B%22close%22%3A1%7D; nfastpromo_open=0; __ddg9_=109.245.36.26; _ym_isad=2; _ym_visorc=w; XSRF-TOKEN=WkIFqBeg6LHv8s7xn5hsoCcl4U8GJanIdp36lIHH; __ddg8_=93RnTiuxPs7LBxJv; __ddg10_=1750703158"
}
response = requests.get(url, headers=headers)

# Создаем файл для записи результатов
output_file = f"rss_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def print_and_write(text, file_handle):
    """Выводит текст в консоль и записывает в файл"""
    print(text)
    file_handle.write(text + '\n')

print("HTTP статус:", response.status_code)
print("Первые 200 символов ответа:")
print(response.text[:400])

if response.status_code == 200:
    with open(output_file, 'w', encoding='utf-8') as f:
        print_and_write(f"Результаты парсинга RSS от {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f)
        print_and_write("=" * 60, f)
        print_and_write("", f)
        
        root = ET.fromstring(response.content)
        for item in root.findall('.//item'):
            title = item.find('title')
            description = item.find('description')
            link = item.find('link')
            pubDate = item.find('pubDate')
            if pubDate is not None:
                print_and_write(f"Дата публикации: {pubDate.text}", f)
            if title is not None:
                print_and_write(f"Заголовок: {title.text}", f)
            if description is not None:
                print_and_write(f"Описание: {description.text}", f)
            if link is not None:
                print_and_write(f"Ссылка: {link.text}", f)
            print_and_write('-' * 40, f)
        
        print_and_write("", f)
        print_and_write(f"Результаты сохранены в файл: {output_file}", f)
else:
    with open(output_file, 'w', encoding='utf-8') as f:
        error_msg = "Ошибка доступа. Возможно, требуется авторизация или сайт блокирует ботов."
        print_and_write(error_msg, f)