a,c=input().split(),0
for i in range(len(a)):
    for j in range(i+1,len(a)):
        if a[i]==a[j]:
            c+=1
print(c)