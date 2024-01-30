s=f"{input()} запретил букву"
for i in list(filter(lambda e:e in s,'абвгдежзийклмнопрстуфхцчшщъыьэюя')):
    print(s+' '+i)
    s=' '.join(s.replace(i,'').split())