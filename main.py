def wisdom_multiplication(x, y, length_check = True):
    c,d=(100-x),(100-y)
    a,s=100-(c+d),str(c*d)
    return str(a)+f'{0 if len(s)==1 and length_check else ""}'+s

print(wisdom_multiplication(99,99,False))