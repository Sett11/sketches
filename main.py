a,b=int(input()),int(input())
print(*[i for i in range(a,b+1) if i%17==0 or (i%3==0 and i%5==0) or str(i)[-1]=='9'],sep='\n')