a,b=int(input()),int(input())
r=[i for i in range(min(a,b),max(a,b)+1)]
print(*(r[::-1] if a>b else r),sep='\n')