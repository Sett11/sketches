from bisect import insort

r=[]

for i in range(int(input())):
    insort(r,int(input()))

print(*r[-2:][::-1],sep='\n')