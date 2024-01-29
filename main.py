a,n,v=[int(input()) for _ in range(int(input()))],int(input()),False
for i in range(len(a)):
    if v:
        break
    for j in range(i+1,len(a)):
        if a[i]*a[j]==n:
            print('ДА')
            v=True
            break
else:
    print('НЕТ')