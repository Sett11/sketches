"""
Обработка результатов для скачивания
Задача: выбрать целевые дял скачивания файлы
Также хорошо бы хранить информацию о скачанных файлах, чтобы исключить или минимизировать затраты на дубли
Надо хранить не только файл, но и мету к нему, полученную из API
"""
import json
from glob import glob

# читаем что есть в json
files=glob('kadr_json/*.json')
results=[]
for fl in files:
    with open(fl, 'r', encoding='utf-8') as f:
        r=json.load(f)
    
    for i in r['items']:
        tj={}
        for k in i.keys():
            if k=='ContentTypes':
                tj[k]=i[k][0]
            else:
                tj[k]=i[k]
        results.append(tj)
print(len(results))

import pandas as pd
df=pd.DataFrame(results)
# отсекли лишние дела, которые нас не интересуют - результат, то что скачиваем
df=df[(df['InstanceLevel']>1) & (df['Type']!='Определение')].copy()
len(df)
