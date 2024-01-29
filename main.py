a,b=float(input()),float(input())
c=a/(b*b)
print('Оптимальная масса' if 18.5<=c<=25 else 'Недостаточная масса' if c<18.5 else 'Избыточная масса')