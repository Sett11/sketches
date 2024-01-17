def foo():
    pass

try:
    foo()
except AssertionError:
    print('AssertionError')
except ZeroDivisionError:
    print('ZeroDivisionError')
except ArithmeticError:
    print('ArithmeticError')