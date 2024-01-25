a,b,c=[],[],[]
for i in range(int(input())):
    n=int(input())
    a.append(n) if n<0 else c.append(n) if n>0 else b.append(n)
print(*(a+b+c),sep='\n')