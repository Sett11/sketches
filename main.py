with open('logfile.txt','r',encoding='utf-8') as h,open('output.txt','w',encoding='utf-8') as o:
    for i in h:
        a,b,c=i.split(', ')
        if abs(float(b.replace(':','.'))-float(c.replace(':','.')))>=1:
            print(a)