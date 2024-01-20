from requests import get

file=open('dataset_24476_3.txt')
a=file.read().strip().split('\n')
file.close()

for i in range(len(a)):
    res=get('http://numbersapi.com/'+a[i]+'/math').text
    if "is a number for which we're missing a fact" in res or "is an uninteresting number" in res or "is an unremarkable number" in res:
        a[i]='Boring'
    else:
        a[i]='Interesting'

with open('solution.txt','w') as w:
    for i in range(len(a)):
        w.write(a[i]+('\n' if i!=len(a)-1 else ''))