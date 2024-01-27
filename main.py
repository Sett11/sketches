from re import sub

print(sub(r'[A-Z]',lambda s:'_'+s.group().lower(),input())[1:])