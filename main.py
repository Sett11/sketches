from bisect import insort

r=[]
for i in range(5):
    insort(r,int(input()))
print(f"Наименьшее число = {r[0]}",f"Наибольшее число = {r[-1]}",sep='\n')