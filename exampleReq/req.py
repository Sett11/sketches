import requests
import time
import asyncio


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


async def fun1(x):
    print(x**2)
    await asyncio.sleep(3)
    print('fun1 завершена')


async def fun2(x):
    print(x**0.5)
    await asyncio.sleep(3)
    print('fun2 завершена')


async def main():
    task1 = asyncio.create_task(fun1(4))
    task2 = asyncio.create_task(fun2(4))

    await task1
    await task2


print(time.strftime('%X'))

asyncio.run(main())

print(time.strftime('%X'))