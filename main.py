f=lambda a,b:len(a)==len(b) and len([i for i,j in enumerate(a) if a[i]!=b[i]])==1

print(f(input(),input()))