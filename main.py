def f(s):
    a=[False]*3+[len(s)>=8]
    for i in s:
        if i.islower():
            a[0]=1==1
        if i.isupper():
            a[1]=1==1
        if i.isdigit():
            a[2]=1==1
    return all(i for i in a)

print(f(input()))