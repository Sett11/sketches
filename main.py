from re import sub
from itertools import permutations

alf='AAABBBCCC'

def f(s):
    return len(sub(r'(.)\1*',lambda x:(k:=x.group())[0]+str(len(k)),s))<len(s)

a=set([''.join(i) for i in permutations(alf)])

print((len(a)-len(list(filter(f,a))))/len(a))