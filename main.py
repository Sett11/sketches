def simple_multiplication(x, y):
    return (100 - ((100-x) + (100-y)))*100 + (100-x)*(100-y)

def wisdom_multiplication(x, y, length_check = True):
    c,d=(100-x),(100-y)
    a,s=100-(c+d),str(c*d)
    return str(a)+f'{0 if len(s)==1 and length_check else ""}'+s

def multiplication_check_list(start=10, stop=99,length_check=True):
    a=sum([[int(simple_multiplication(i,j))==int(wisdom_multiplication(i,j,length_check)) for j in range(start,stop+1)] for i in range(start,stop+1)],[])
    c=a.count(False)
    print(f'Правильных результатов: {len(a)-c}',f'Неправильных результатов: {c}',sep='\n')

print(multiplication_check_list(98,99,False))