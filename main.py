r=[]
with open(sheet,'r',encoding='utf-8') as f:
    for i in f.readlines():
        p=i.split()
        if p[-1]=='(экзамен)' or p[-1]=='(автомат)':
            r.append(int(p[-2]))
t=sum(r)/len(r)
with open(mean,'r',encoding='utf-8') as f:
    x=sum(map(int,f.read().strip()))
    if x==t:
        print('OK')
    else:
        print('ERROR')