def draw_triangle(q,k):
    n=k//2+(1 if k&1 else 0)
    a=[q*i for i in range(1,n+1)]
    a+=a[::-1][1:]
    return '\n'.join(a)

fill = input()
base = int(input())

print(draw_triangle(fill, base))