import requests

s=requests.get('https://stepik.org/media/attachments/course67/3.6.3/699991.txt')

while True:
    if s.text.startswith('We'):
        print(s.text)
        break
    s=requests.get('https://stepik.org/media/attachments/course67/3.6.3/'+s.text)