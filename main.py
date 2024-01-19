from re import findall
from requests import get

s,r=input(),set()
reg=r'(<a.*href=[\'"])(\w+://)?(\w[a-zA0-9.-]+)'
q=get(s.strip()).text
a=findall(reg,q)
for i in a:
    r.add(i[2])
for i in sorted(r):
    print(i)