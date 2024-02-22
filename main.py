arithmetic_operation =lambda x:lambda a,b:eval(f'{a}{x}{b}')

add = arithmetic_operation('+')
div = arithmetic_operation('/')
print(add(10, 20))
print(div(20, 5))