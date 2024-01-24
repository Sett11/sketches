f=lambda x:x if len(str(x))==1 else f(sum(map(int,str(x))))

print(f(int(input())))