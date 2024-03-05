import requests
from pprint import pprint


headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
data={'custname':'Jhonny','custtel':'fffooottt','custemail':'mail@jonny.ru','size':'large','topping':'bacon'}
response=requests.post('https://httpbin.org/post',headers=headers)

pprint(dir(requests))
#pprint(help(response))