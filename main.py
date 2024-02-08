a = {'a': 100, 'z': 333, 'b': 200, 'c': 300, 'd': 45, 'e': 98, 't': 76, 'q': 34, 'f': 90, 'm': 230}
b = {'a': 300, 'b': 200, 'd': 400, 't': 777, 'c': 12, 'p': 123, 'w': 111, 'z': 666}

result = {i:a[i]+b[i] if i in a and i in b else a.get(i,b.get(i)) for i in set(list(a.keys())+list(b.keys()))}
print(result)