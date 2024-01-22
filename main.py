a,b,c=input(),input(),input()
try:
    print(eval(a+(c+b if c in '+-*/' else "/'aaa'")))
except ZeroDivisionError:
    print('На ноль делить нельзя!')
except TypeError:
    print('Неверная операция')