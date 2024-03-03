from string import digits,ascii_uppercase

def cb(n,b):
    a,r=digits+ascii_uppercase,''
    while n:
        r=a[n%b]+r
        n//=b
    return r

def convert(n,tb=10,fb=10):
    return cb(int(str(n),fb),tb)
    


print(convert(42))
print(convert('2A',16))