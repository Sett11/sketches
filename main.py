from collections import Counter

s,r=set(),[]

for i in range(1,33):
    for j in range(1,33):
        if i!=j:
            r.append(i**3+j**3)

print(sorted(list(map(lambda e:e[0],filter(lambda x:x[1]==4,Counter(r).items())))))