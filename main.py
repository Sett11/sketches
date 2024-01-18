def check_prime(n):
    return n>=2 and all(n%i for i in range(2,int(n**.5+1)))

def primes():
    n=2
    while True:
        if check_prime(n):
            yield n
        n+=1

p=primes()
print(next(p))
print(next(p))
print(next(p))
print(next(p))
print(next(p))
print(next(p))
print(next(p))
print(next(p))