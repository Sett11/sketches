k=0
with open('grades.txt') as f:
    for i in f:
        a=list(i.split())
        if all(int(j)>=65 for j in map(int,a[1:])):
            k+=1
print(k)