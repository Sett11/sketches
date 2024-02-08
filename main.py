d={1:'AEILNORSTU',2:'DG',3:'BCMP',4:'FHVWY',5:'K',8:'JX',10:'QZ'}
t,s=0,input()
for i in s:
    for j in d:
        if i in d[j]:
            t+=j
            break
print(t)