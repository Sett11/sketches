from requests import get
from json import loads

header={"X-Xapp-Token":"eyJhbGciOiJIUzI1NiJ9.eyJyb2xlcyI6IiIsInN1YmplY3RfYXBwbGljYXRpb24iOiI1ZjhlNDBhNC0yNjMxLTQwNGEtYTJjYi0xYmQ1MjQ4MDU0NTciLCJleHAiOjE3MDYzNTk3ODQsImlhdCI6MTcwNTc1NDk4NCwiYXVkIjoiNWY4ZTQwYTQtMjYzMS00MDRhLWEyY2ItMWJkNTI0ODA1NDU3IiwiaXNzIjoiR3Jhdml0eSIsImp0aSI6IjY1YWJjMTY4YTVlNmU5MDAwYjYwODJiYyJ9.apICD_NbaGqssVKZg23R5bb0HvItZEhQ-SrCbu7i5WM"}

q,res=[],[]
f=open('dataset_24476_4.txt','r',encoding='utf-8')
q=f.read().strip().split('\n')
f.close()

for i in q:
    r=get("https://api.artsy.net/api/artists/"+i,headers=header)
    l=loads(r.text)
    res.append((l['sortable_name'],l['birthday']))

res.sort(key=lambda x:(x[1],-ord(x[0][0])))

with open('solve.txt','w',encoding='utf-8') as s:
    for i in res:
        s.write(i[0]+'\n')