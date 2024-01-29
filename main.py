from re import sub

print(','.join(sub(r'.{3,3}',lambda x:x.group()+' ',input()[::-1]).split())[::-1])