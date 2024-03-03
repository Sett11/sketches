def kaprekar(n):
    k=str(n**2)
    for i in range(1,len(k)):
        a,b=int(k[:i]),int(k[i:])
        if int(k[:i])+int(k[i:])==n and (a and b):
            return True
    return False

print(kaprekar(297))