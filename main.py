# graph = [{"name": "B", "parents": ["A", "C", "D"]},
#          {"name": "C", "parents": ["A"]},
#          {"name": "A", "parents": []},
#          {"name": "D", "parents": ["A", "E"]},
#          {"name": "E", "parents": ["F", "G"]},
#          {"name": "F", "parents": []},
#          {"name": "G", "parents": ["F"]}]
# d=[{"name": "A", "parents": []}, {"name": "B", "parents": ["A", "C"]}, {"name": "C", "parents": ["A"]}]

from json import loads
def gen_graph(a):
    d={i['name']:{'parents':i['parents'],'children':[]} for i in a}
    for i in range(len(a)):
        for j in a[i]['parents']:
            d[j]['children'].append(a[i]['name'])
    return d,[i for i in d]

a,b=gen_graph(loads(input()))

def count(g,x,q):
    if not g[x]['children']:
        return q
    for i in g[x]['children']:
        q.append(i)
        count(g,i,q)
    return q

def f(a,b):
    r=[]
    for i in b:
        r.append((i,len(set(count(a,i,[])))+1))
    return sorted(r)

for i in f(a,b):
    print(f'{i[0]} : {i[1]}')