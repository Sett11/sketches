from fractions import Fraction as f
a,b=input(),input()

print(f'{a} + {b} = {f(a)+f(b)}')
print(f'{a} - {b} = {f(a)-f(b)}')
print(f'{a} * {b} = {f(a)*f(b)}')
print(f'{a} / {b} = {f(a)/f(b)}')