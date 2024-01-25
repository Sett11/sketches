n=int(input())
a=[int(input()) for i in range(n)]
print([j for i,j in enumerate(a) if i%2==0])