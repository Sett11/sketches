common=lambda a,b:list(set(a)&set(b))

print(common([0, 2, 3, 4, 5, 19, 42],[0, 6, 19, 33, 42, 55, 66, 77, 99, 101, 256]))