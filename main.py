with open(input(),'r',encoding='utf-8') as f:
    t=0
    for i in f.readlines():
        t+=int(i.strip())
    print(t)