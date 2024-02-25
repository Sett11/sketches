from collections import Counter as c
with open('goats.txt','r',encoding='utf-8') as h,open('answer.txt','w',encoding='utf-8') as o:
    v,a=False,[]
    for i in h:
        i=i.strip()
        if v:
            a.append(i)
        if i=='GOATS':
            v=True
    d=c(a)
    for i in d:
        if d[i]>(len(a)/100*7):
            o.write(i+'\n')