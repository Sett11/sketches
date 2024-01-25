f=lambda x:x**2+2*x+1
a=[int(input()) for _ in range(int(input()))]
print(*a,sep='\n')
print()
print(*map(f,a),sep='\n')