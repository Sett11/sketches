mean=lambda *args:sum(a:=[i for i in args if type(i) in (int,float)])/(len(a) or 1)

print(mean(1.5, True, ['stepik'], 'beegeek', 2.5))
print(mean(True,['stepik'], 'beegeek'))