import os

event,file_name='aaa','txt.log'
x=''

if os.path.isfile(file_name):
    with open(file_name,'r',encoding='utf-8') as f:
        x=f.read()

with open(file_name,'w',encoding='utf-8') as f:
    if x:
        n=int(x.split()[1])+1
    else:
        n=1
    f.seek(0)
    f.write(f"event {n} - '{event}'\n"+x)