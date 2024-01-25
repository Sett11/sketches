from collections import OrderedDict

print(*OrderedDict().fromkeys([input() for _ in range(int(input()))]).keys(),sep='\n')