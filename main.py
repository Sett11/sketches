from bisect import insort

r=[]
for i in range(3):
    insort(r,int(input()))
    
print(*r[::-1],sep='\n')