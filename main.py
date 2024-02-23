a=[]
with open('data.txt', encoding='utf-8') as file:
    a=file.readlines()
print(*map(str.strip,a[::-1]),sep='\n')