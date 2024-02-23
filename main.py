a,m=[],0
with open('lines.txt', encoding='utf-8') as file:
    for i in file:
        s=i.strip()
        m=max(m,len(s))
        a.append(s)
print(*[i for i in a if len(i)==m],sep='\n')