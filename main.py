from calendar import monthrange

f=lambda n:monthrange(2023,n)[1]

print(f(int(input())))