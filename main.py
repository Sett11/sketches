from string import digits as d
def translate(n,b=2):
    r=''
    while n:
        r=d[n%b]+r
        n//=b
    return r

print(translate(19))