product,count=1,0
for i in range(10):
    n=int(input())
    if n>=0:
        product*=n
        count+=1
if count>0:
    print(count,product,sep='\n')
else:
    print('NO')