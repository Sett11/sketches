import numpy as np

def ferh_eq(n):
    r,x,a=2.5,.25,[[1]*n for _ in range(n)]
    f=lambda x:'\n'.join(''.join('-' if j==1 else '+' for j in i) for i in zip(*x))
    ff=lambda x:sum((sum(i)-n)/len(i) for i in x)/len(x)
    while r<4:
        for i in range(1,100):
            x=r*x*(1-x)
            if i>50:
                xs=round(((r-2.5)/1.5)*(n-1))
                ys=round((1-x)*(n-1))
                a[xs][ys]+=1
        r+=.0001
        d=np.linalg.det(a)
        if d:
            print(True,d,r,ff(a))
            return f(a)
    print(False,f(a),sep='\n')
    return r,ff(a)

print(ferh_eq(111))