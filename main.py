from re import sub,IGNORECASE
s=set()
with open('forbidden_words.txt','r',encoding='utf-8') as d:
    s.update(d.read().split())
with open(input()) as x:
    a=x.read()
    for i in s:
        a=sub(i,lambda c:'*'*len(c.group()),a,flags=IGNORECASE)
    print(a)