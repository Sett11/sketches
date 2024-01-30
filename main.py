from re import sub

s=input()
print(max(map(int,sub(r'(.)\1*',lambda x:' '+str(len(x.group())) if x.group()[0]=='Р' else '',s).split()),default=0))