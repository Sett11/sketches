a,b,c=input(),input(),input()

def f(a,b,c):
    if b not in a:
        return 0
    if b==c:
        return 'Impossible'
    i=0
    while b in a:
        if i>=1000:
            return 'Impossible'
        a=a.replace(b,c)
        i+=1
    return i
    

print(f(a,b,c))