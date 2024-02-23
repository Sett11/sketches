with open('population.txt',encoding='utf-8') as f:
    for i in f.readlines():
        a,b=i.split('\t')
        if a[0]=='G' and int(b.strip())>5e5:
            print(a)