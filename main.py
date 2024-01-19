import csv

r,o,c=[],{},0

with open('Crimes.csv','r') as s:
    r=list(csv.reader(s))

for i in r:
    j=i[2].split()
    if j[0].split('/')[-1]=='2015':
        if i[5] not in o:
            o[i[5]]=1
        else:
            o[i[5]]+=1
        c=max(c,o.get(i[5]))

print([i for i in o if o[i]==c][0])