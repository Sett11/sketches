with open('class_scores.txt','r',encoding='utf-8') as h,open('new_scores.txt','w',encoding='utf-8') as o:
    for i in h:
        a,b=i.split()
        o.write(f'{a} {min(int(b)+5,100)}\n')