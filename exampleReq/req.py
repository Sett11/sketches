import requests
import time
import asyncio
import threading
import multiprocessing
import os
import random


# 1
# Делаем get-запрос в google, получаем ответ, разбираем ответ в виде гипертекста html, записываем его в файл index.html
# params={'q':'dzen python'}
# response=requests.get('https://google.com/search',params=params, allow_redirects=True)
# if response:
#     with open('index.html','w',encoding='utf-8') as f:
#         if f.writable():
#             f.write(response.text)

# 2
# Делаем post-запрос на сайт httpbin.org. В запросе передаём headers, в котором указываем данные о нас, как о пользователе,
# чтобы сайт интерпретировал нас, как обычного пользователя. Целью запроса является заполнение html-формы и мы передаём в date данные,
# необходимые для заполнения этой формы. После получения ответа выводим данные в формате json, что в данном случае означает словарь.
# data={'custemail':'ddd@mail.com','custname':'Jhonny','custtel':'111','size':'large','topping':'bacon'}
# headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
# response=requests.post('https://httpbin.org/post',data=data,headers=headers)
# print(response.json()['form'])

# 3
# Подключаемся в рамках сессии к ресурсу jsonplaceholder и формируем запросы
# with requests.session() as s:
#     response=requests.get('https://jsonplaceholder.typicode.com/users')
#     if response:
#         for i in response.json():
#             print(i['name'])
#     response=requests.get('https://jsonplaceholder.typicode.com/comments')
#     if response:
#         for i in response.json():
#             print(i['body'][:5])


# 4 multiprocessing Пример разделения выполнения программы на разные процессы (если количество ядер позволяет)
# Примечание - в случае использования процессов способ запуска является принципиальным, иначе приводит к неблокирующей ошибке
# В нашем случае работает не вполне корректно, возможно ввиду малого количества ядер. 

# def f(n):
#     s = random.randrange(1,10)
#     time.sleep(s)
#     print(f"I am Worker {n}, i slept for {s} seconds")

# if __name__=='__main__':
#     for i in range(2):
#         f(i)
    
#     print("All Processes are queued, let's see when they finish!")

# if __name__=='__main__':

#     for i in range(2):
#         t = multiprocessing.Process(target=f,args=(i,))
#         t.start()
#         t.join()

#     print("All Processes are queued, let's see when they finish!")


# 5 threading Пример разделения выполнения программы на разные потоки

# def f(n):
#     sec=random.randrange(1,10)
#     time.sleep(sec)
#     print(f'I am Worker {n}, i slept for {sec} seconds')

# синхронная версия
# for i in range(5):
#     f(i)

# мультипоточная версия
# for i in range(5):
#     t=threading.Thread(target=f,args=(i,))
#     t.start()

# print('All Threads finiched???')

# 6 Пример синхронного (последовательного) выполнения программы
# def f1(n):
#     print('f1 start')
#     print(n**2)
#     time.sleep(3)
#     print('f1 comleted')

# def f2(n):
#     print('f2 start')
#     print(n**.5)
#     time.sleep(3)
#     print('f2 comleted')

# def main():
#     print('Start main')
#     f1(5),f2(5)
#     print('Comleted main')

# print(time.strftime('%X'))
# main()
# print(time.strftime('%X'))

# 6.1 asyncio Пример асинхронного (непоследовательного) выполнения программы
# async def f1(n):
#     print('f1 start')
#     print(n**2)
#     await asyncio.sleep(3)
#     print('f1 comleted')

# async def f2(n):
#     print('f2 start')
#     print(n**.5)
#     await asyncio.sleep(3)
#     print('f2 comleted')

# async def main():
#     print('Start main')
#     a=asyncio.create_task(f1(5))
#     b=asyncio.create_task(f2(5))
#     await a, await b
#     print('Comleted main')

# print(time.strftime('%X'))
# asyncio.run(main())
# print(time.strftime('%X'))