d={}
r=[]

def f(a,b,q):
    if a not in d or not d[a].get('children'):
        q.append('No')
        return q
    if b in d[a]['children']:
        q.append('Yes')
        return q
    for i in d[a].get('children',[]):
        f(i,b,q)
    return q

for _ in range(int(input())):
    s=input().split(' : ')
    t=s.pop(0)
    if s:
        s=s[0].split()
    if t not in d:
        d[t]={'parents':[*s],'children':[]}
    else:
        d[t]['parents'].extend([*s])
    if s:
        for i in s:
            if i not in d:
                d[i]={'parents':[],'children':[t]}
            else:
                d[i]['children'].append(t)

for i in range(int(input())):
    s,v=input(),False
    for j in r:
        if all(k=='No' for k in f(j,s,[])):
            continue
        else:
            v=True
    if v:
        print(s)
    r.append(s)