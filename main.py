def numerics(n):
    return list(map(int,str(n)))

def kaprekar_step(L):
    L.sort()
    return int(''.join(map(str,L[::-1])))-int(''.join(map(str,L)))

def kaprekar_loop(n):
    print(n)
    while n!=6174:
        n=kaprekar_step(numerics(n))
        print(n)

print(kaprekar_loop(8654))