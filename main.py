def numerics(n):
    return list(map(int,str(n)))

def kaprekar_check(n):
    s=str(n)
    return len(s) in (3,4,6) and len(set(s))!=1 and n not in [100,1000,100000]

def kaprekar_step(L):
    L.sort()
    return int(''.join(map(str,L[::-1])))-int(''.join(map(str,L)))

def kaprekar_loop(n):
    if n==1000:
        print("Ошибка! На вход подано число 1000")
        return
    if len(set(numerics(n)))==1:
        print(f"Ошибка! На вход подано число {n} - все цифры одинаковые")
        return
    print(n)
    while n!=6174:
        n=kaprekar_step(numerics(n))
        print(n)

print(kaprekar_loop(1000))