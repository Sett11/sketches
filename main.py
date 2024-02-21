a,x=list(map(int,(input().split()))),int(input())
l=len(a)-1
print(sum([j*x**(l-i) for i,j in enumerate(a)]))