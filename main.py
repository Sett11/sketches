a=sorted(map(int,input()),reverse=True)
try:
    print(next(i for i in a if i%3==0))
except StopIteration:
    print('NO')