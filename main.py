a=[i for i,j in enumerate(input()) if j=='f']
print(a[1] if len(a)>1 else -1 if len(a)==1 else -2)