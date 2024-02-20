mean=lambda *args,f=lambda a:list(filter(lambda x:type(x) in (int,float),a)):sum(f(args))/(len(f(args)) or 1)

print(mean(1.5, True, ['stepik'], 'beegeek', 2.5))
print(mean(True,['stepik'], 'beegeek'))