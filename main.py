greet=lambda s,*args:'Hello, '+' and '.join([s]+list(args))+'!'

print(greet('beegeek'))
print(greet('stepik', 'beegeek'))
print(greet('beegeek','a','b'))