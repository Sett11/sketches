d={}

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
    else:
        d[t]['parents'].append(t)

for i in range(int(input())):
    v=f(*input().split(),[])
    if v is None:
        print('No')
    else:
        print('No' if all(k=='No' for k in v) else 'Yes')

# d={'Obj': {'parents': [], 'children': ['A', 'B', 'C']}, 'A': {'parents': ['Obj'], 'children': ['F', 'K']}, 'B': {'parents': ['Obj'], 'children': ['K', 'Z']}, 'C': {'parents': ['Obj'], 'children': ['G']}, 'F': {'parents': ['A'], 'children': ['L']}, 'K': {'parents': ['A', 'B'], 'children': ['L']}, 'Z': {'parents': ['B'], 'children': ['P']}, 'G': {'parents': ['C'], 'children': ['N']}, 'L': {'parents': ['F', 'K'], 'children': ['P']}, 'N': {'parents': ['G'], 'children': ['P']}, 'P': {'parents': ['L', 'Z', 'N'], 'children': []}}

# print(f('Obj','B',[]))