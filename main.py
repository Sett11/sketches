from decimal import Decimal as d
print(all(x[0]**2+x[1]**2+x[2]**2<=4 for x in zip([d(i) for i in input().split()],[d(i) for i in input().split()],[d(i) for i in input().split()])))