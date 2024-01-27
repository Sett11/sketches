from re import sub

s=sub(r'[\s.,!?-]','',input().lower())
print(s==s[::-1])