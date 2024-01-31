from re import sub

print([list(i) for i in sub(r'(.)\1*',lambda x:' '+x.group()+' ',''.join(input().split())).split()])