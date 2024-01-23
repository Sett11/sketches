total,c=1,'-'

for i in range(2,int(input())+1):
    total=total-i if c=='-' else total+i
    c='+' if c=='-' else '-'

print(total)