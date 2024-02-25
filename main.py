f=input()
a,r=[],[]
with open(f,encoding='utf-8') as f:
    for i in f:
        t=i.strip()
        if t:
            a.append(t)
if a[0].startswith('def'):
    r.append(a[0].replace('def ',''))
    r[0]=r[0][:r[0].index('(')]
for i in range(1,len(a)):
    if a[i].startswith('def') and not a[i-1].startswith('#'):
        t=a[i].replace('def ','')
        t=t[:t.index('(')]
        r.append(t)
if r:
    print(*r,sep='\n')
else:
    print('Best Programming Team')