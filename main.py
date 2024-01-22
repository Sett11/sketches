n=int(input())
a,b='красный','черный'
if n>0 and (n<11 or 18<n<29):
    print(a if n&1 else b)
elif n<37 and (11<=n<19 or n>28):
    print(b if n&1 else a)
elif not n:
    print('зеленый')
else:
    print('ошибка ввода')