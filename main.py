a=['*'*i for i in range(1,int(input())//2+2)]
print(*(a+a[::-1][1:]),sep='\n')