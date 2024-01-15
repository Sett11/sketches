closest_mod_5=lambda x:next(i for i in range(x,int(1e9)) if i%5==0)

print(closest_mod_5(5))