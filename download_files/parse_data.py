"""
Задача: написать скрипт, который по крону запускается в докере и на мапированный диск складывает JSON
- собирает данные за вчерашний день
- если остаются запросы идет в прошлое
- состояние последнего прошлого надо хранить или запрашивать наиболее раннюю дату, например в уже сохраненных json, хотя хранить их отдельно не будем долго, но не удаляем пока
"""
import requests
from datetime import datetime, timedelta
import time
import json
from tqdm.auto import tqdm

# лимитирование количества запросов
# хорошо бы поставить проверку на лимиты и запрашивать их
count=200
start_date=datetime.now() № # дата начала

def save_json(j, date_save, page):
    # сохраняет данные в json
    s = date_save.strftime('%Y-%m-%d')
    with open(f"kadr_json/{s}-{page}.json", 'w', encoding='utf-8') as f:
        json.dump(j, f)
# Итерации по дням, так как часто количество результатов больше, чем может выдать система
for t in tqdm(range(1,10), total=5):
    s = start_date.strftime('%Y-%m-%d')
    to_date=s
    from_date=(start_date-timedelta(days=1)).strftime('%Y-%m-%d')
    # получаем первую страницу и смотрим, сколько там еще...
    url="https://service.api-assist.com/parser/ras_arbitr_api/?key=997834c96856bb3783da8c42a59d06b3&DateFrom={from_date}&DateTo={to_date}&Page=1&Text='решение'"
    r=requests.get(url.format(from_date=from_date, to_date=to_date))
    save_json(r.json(), start_date, 1)
    count-=1
    time.sleep(1) # чтобы не перегружать APi ребятам
    # идем по страницам
    for p in range(2, r.json()['pages']):
        if count<1:
            break
        url="https://service.api-assist.com/parser/ras_arbitr_api/?key=997834c96856bb3783da8c42a59d06b3&DateFrom={from_date}&DateTo={to_date}&Page={p}&Text='решение'"
        r=requests.get(url.format(from_date=from_date, to_date=to_date, p=p))
        save_json(r.json(), start_date, p)       
        time.sleep(1)
    start_date=(start_date-timedelta(days=1))


# Это код, который бежит по дням и собирает метаданные и ссылки, используем стороннее api