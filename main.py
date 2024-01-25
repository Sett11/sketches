from collections import Counter

print(max(map(lambda x:(x[1],x[0]),Counter(input()).items()))[1])