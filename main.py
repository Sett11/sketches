d={'север':0,'юг':0,'восток':0,'запад':0}
for i in range(int(input())):
    a,b=input().split()
    d[a]+=int(b)
print(d['восток']-d['запад'],d['север']-d['юг'])