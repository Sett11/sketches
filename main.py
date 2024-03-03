def numerics(n):
    return list(map(int,str(n)))

def kaprekar_check(n):
    s=str(n)
    return len(s) in (3,4,6) and len(set(s))!=1 and n not in [100,1000,100000]

def kaprekar_step(L):
    L.sort()
    return int(''.join(map(str,L[::-1])))-int(''.join(map(str,L)))


def kaprekar_loop(n):
    if not kaprekar_check(n):
        print(f"Ошибка! На вход подано число {n}, не удовлетворяющее условиям процесса Капрекара")
        return
    r=[]
    print(n)
    while n not in (495, 6174, 549945, 631764):
        n=kaprekar_step(numerics(n))
        if n in r:
            print(f'Следующее число - {n}, кажется процесс зациклился...')
            return
        r.append(n)
        print(n)

print(kaprekar_loop(1000))