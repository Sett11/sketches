from random import randint
print(*[randint(1000000,9999999) for _ in range(100)],sep='\n')