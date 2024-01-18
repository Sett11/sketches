def mod_checker(x,mod=0):
    f=lambda y:y%x==mod
    return f

mod_3=mod_checker(3)

print(mod_3(3))
print(mod_3(4))