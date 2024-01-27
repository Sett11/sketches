a,b,c=int(input()),int(input()),int(input())
d=b**2-4*a*c
q=d**.5
if d==0:
    n=-b/(2*a)
    print(n,n)
else:
    print(*sorted([(-b-q)/(2*a),(-b+q)/(2*a)]))