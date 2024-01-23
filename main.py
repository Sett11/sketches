r=[]
x=10
for i in range(1,x):
    for j in range(1,x):
        for k in range(1,x):
            if 28*i+30*j+31*k==365:
                r.append((i,j,k))

print(r)