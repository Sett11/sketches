def multiplication_check_list(start=10, stop=99):
    a=sum([[bool(i*j) for j in range(start,stop+1)] for i in range(start,stop+1)],[])
    c=a.count(0)
    print(f'Правильных результатов: {len(a)-c}',f'Неправильных результатов: {c}',sep='\n')

multiplication_check_list(96,97)