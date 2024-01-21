n=int(input())
a=['детство','молодость', 'зрелость','старость']
print(a[0] if n<15 else a[1] if n<25 else a[2] if n<60 else a[3])