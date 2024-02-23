def read_csv():
    a=[]
    with open('data.csv',encoding='utf-8') as f:
        for i in f.readlines():
            a.append(list(map(str.strip,i.split(','))))
    b=a.pop(0)
    for i in a:
        for j in range(len(i)):
            i[j]=(b[j],i[j])
    return list(map(dict,a))

print(read_csv())