from random import randint
with open('input.txt','r',encoding='utf-8') as h,open('output.txt','w',encoding='utf-8') as o:
    j=1
    for i in h:
        o.write(f'{j}) {i}')
        j+=1