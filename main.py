from random import choice

file=open('lines.txt','r',encoding='utf-8')
print(choice(file.readlines()).rstrip())
file.close()