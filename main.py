def f(s,k='anton'):
    n,r=0,[]
    for i in range(5):
        n=s.find(k[i],n)
        r.append(n)
    return all(i!=-1 for i in r)
print(*[j+1 for j,k in enumerate([input() for _ in range(int(input()))]) if f(k)])