n=int(input())%(1440*3600)
a=n//3660
n-=a*3600
b=n//60
n-=b*60
print(*([a]+list(map(lambda s:f'{0 if s<10 else ""}{s}',[b,n]))),sep=':')