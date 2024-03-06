from string import digits,ascii_uppercase

def cb(n,b):
    a,r=digits+ascii_uppercase,''
    while n:
        r=a[n%b]+r
        n//=b
    return r

        
def kaprekar(n,base=10):
    c=int(str(n),base)
    k=cb(c**2,base)
    for i in range(1,len(k)):
        a,b=int(k[:i],base),int(k[i:],base)
        if a+b==c and (a and b):
            return True
    return False

print(kaprekar('F',16))