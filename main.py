from requests import get
from re import findall,search

a,b=input(),input()
c=get(a).text
v='No'
r=findall(r'https:.+\.html',c)
for i in r:
    if b.replace('stepik.org','stepic.org') in search(r'https:.+\.html',get(i).text).group():
        v='Yes'
print(v)