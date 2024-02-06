from re import sub
print(len(set(sub(r'[.,:;\-?!]','',input().lower()).split())))