a,b,c=float(input()),float(input()),float(input())
d=b**2-4*a*c
q=d**.5
if d==0:
    print(-b/(2*a))
elif d>0:
    print(*sorted([(-b-q)/(2*a),(-b+q)/(2*a)]),sep='\n')
else:
    print('Нет корней')