from random import sample
a=sample(range(1,76),25)
a[12]=0
print(*[''.join(map(lambda s:str(s).ljust(3),a[i:i+5])) for i in range(0,25,5)],sep='\n')