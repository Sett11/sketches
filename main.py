from collections import Counter
from re import sub
print(sorted(Counter(sub(r'[.,\-:;!?]','',input().lower()).split()).items(),key=lambda x:(x[1],x[0]))[0][0])