from random import choice

with open('first_names.txt',encoding='utf-8') as f,open('last_names.txt',encoding='utf-8') as c:
    a,b=f.readlines(),c.readlines()
    for i in range(3):
        print(choice(a).strip(),choice(b).strip())