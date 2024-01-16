d={'global':{'par':None,'vars':[]}}

def f(x,y):
    if d[x]['par'] is None and y not in d[x]['vars']:
        return None
    if y in d[x]['vars']:
        return x
    return f(d[x]['par'],y)

for _ in range(int(input())):
    a,b,c=input().split()
    if a=='add':
        d[b]['vars'].append(c)
    if a=='create':
        d[b]={'par':c,'vars':[]}
    if a=='get':
        print(f(b,c))