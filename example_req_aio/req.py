import requests
from html.parser import HTMLParser
from pprint import pprint
from bs4 import BeautifulSoup
from random import randrange


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
# 
# data={'custemail':'ddd@mail.com','custname':'Jhonny','custtel':'111','size':'large','topping':'bacon'}
# headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
# response=requests.post('https://httpbin.org/post',data=data,headers=headers)
# print(response.json()['form'])

# 3
# Подключаемся в рамках сессии к ресурсу jsonplaceholder и формируем запросы
# 
# with requests.session() as s:
#     response=s.get('https://jsonplaceholder.typicode.com/users')
#     if response:
#         for i in response.json():
#             print(i['name'])
#     response=s.get('https://jsonplaceholder.typicode.com/comments')
#     if response:
#         for i in response.json():
#             print(i['body'][:5])

# В рамках сессии делаем запрос на лидерборд кодварса, получаем гипертекстовый документ, разбираем его при помощи парсера
# и сохраняем в список имена всех пользователей включённых в лидерборд

# name_users_leaders=[]

# class Parser(HTMLParser):
#     def handle_starttag(self, tag, attrs):
#         if tag=='tr':
#             for i,j in attrs:
#                 if i=='data-username':
#                     name_users_leaders.append(j)

# P=Parser()

# with requests.session() as s:
#     response=s.get('https://www.codewars.com/users/leaderboard')
#     if response:
#         P.feed(response.text)

# pprint(name_users_leaders)

# В рамках сессии делаем запрос на сайт с анекдотами, а именно на страницу с лучшими анекдотами за случайный день, получаем
# гипертекстовый документ, затем при помощи библиотеки beautifulsoup4 разбираем html и получаем все анекдоты со страницы в виде списка

# jokes=[]

# with requests.session() as s:
#     n,k=randrange(1,13),randrange(1,29)
#     url=f"https://www.anekdot.ru/best/anekdot/{str(n).rjust(2,'0')}{str(k).rjust(2,'0')}"
#     response=s.get(url)
#     if response:
#         soup=BeautifulSoup(response.text)
#         list_soup=soup.find_all('div',class_='text',string=True)
#         for i in list_soup:
#             jokes.append(i.get_text())

# print(*jokes,sep='\n')