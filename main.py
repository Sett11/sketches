d={'1': '.,?!:', '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL', '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ', '0': ' '}
s,r=input().upper(),''
for i in s:
    for j in d:
        if i in d[j]:
            r+=j*(d[j].index(i)+1)
print(r)