a,b,c=int(input()),int(input()),int(input())
p=(a+b+c)
pp=p/2
print(p,(pp*((pp-a)*(pp-b)*(pp-c)))**.5,sep='\n')