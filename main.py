import random
import re
import requests
from bs4 import BeautifulSoup
import lxml
import json
import csv
from time import sleep

# url = 'https://health-diet.ru/table_calorie/'
#
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}
req = requests.get(url, headers=headers)
src = req.text
print(src)

with open('index.html', 'w') as file:
    file.write(src)

with open('index.html', 'r') as file:
     src = file.read()

soup = BeautifulSoup(src, 'lxml')

all_categories_dict = {}
all_products_hrefs = soup.find_all('a', class_='mzr-tc-group-item-href')
for item in all_products_hrefs:
    item_text = item.text
    item_href = 'https://health-diet.ru' + item.get('href')
    all_categories_dict[item_text] = item_href

with open('../all_categories_dict.json', 'w', encoding="utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open('../all_categories_dict.json', 'r', encoding='utf-8') as file:
    all_categories = json.load(file)

count = 1
iteration_count = len(all_categories) - 1
print(f'Всего итерация {iteration_count}')

for category_name, category_link in all_categories.items():
    product_info = {}
    category_name = re.sub(r'[\,\.\-\s\'\[\]]', '_', category_name)
    req = requests.get(url=category_link, headers=headers)
    src = req.text

    with open(f'data/{count}_{category_name}.html', 'w', encoding='utf-8') as file:
        file.write(src)


    with open(f'data/{count}_{category_name}.html', 'r', encoding='utf-8') as file:
        src = file.read()
        heads = []

        soup = BeautifulSoup(src, 'lxml')

        # проверка наличия таблицы
        alert_block = soup.find(class_='uk-alert-danger')
        if alert_block is not None:
            continue

        for line in soup.find('thead').find_all('th'):
            heads.append(line.get_text(strip=True))
        with open(f'data/{count}_{category_name}.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(heads)
            for line in soup.find('tbody').find_all('tr'):
                row = []
                for mark in line.find_all('td'):
                    row.append(mark.get_text(strip=True))
                writer.writerow(row)
                product_info[heads[0]] = row[0]
                product_info[heads[1]] = row[1]
                product_info[heads[2]] = row[2]
                product_info[heads[3]] = row[3]
                product_info[heads[4]] = row[4]
        with open(f'data/{count}_{category_name}.json', 'w', encoding='utf-8') as file:
            json.dump(product_info, file, indent=4, ensure_ascii=False)

    print(f'Спарсено {count} из {iteration_count} тем')
    count += 1
    sleep(random.randrange(2, 4))
print('Работа завершена')