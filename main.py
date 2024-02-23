from re import sub
a=[]

with open('file.txt', encoding='utf-8') as file:
    a=list(map(str.strip,file.readlines()))
print('Input file contains:',f"{len(''.join([sub(r'[^A-z]','',i) for i in a]))} letters",f'{sum([len(i.split()) for i in a])} words',f'{len(a)} lines',sep='\n')