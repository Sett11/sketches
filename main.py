from random import randint
print('A'+''.join(chr(randint(97,122)) for _ in range(int(input())-1)))