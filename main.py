n=int(input())
i=j=k=0
while i+k<=n:
    i+=k
    j+=1
    k=int(input())
print('Довольно!',i,j-1,sep='\n')