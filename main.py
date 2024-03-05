f=lambda:sorted([int(i) for i in input().split()])
c,a,d,b,t,i=input(),f(),input(),f(),0,0
while i<len(a):
    j=0
    while j in range(len(b)):
        if abs(a[i]-b[j])<=1:
            a.pop(i)
            b.pop(j)
            t+=1
            i-=1
            break
        j+=1
    i+=1   
print(t)