def merge(a):
    r,d=set(sum([list(i.keys()) for i in a],[])),{}
    for i in r:
        t=set()
        for j in a:
            if i in j:
                t.add(j[i])
        d[i]=t
    return d

print(merge([{'a': 1, 'b': 2}, {'b': 10, 'c': 100}, {'a': 1, 'b': 17, 'c': 50}, {'a': 5, 'd': 777}]))