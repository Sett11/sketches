a=[input() for i in range(int(input()))]
b=[i for i in a if i[-1] in '45']
print(*a,sep='\n')
print('')
print(*b,sep='\n')