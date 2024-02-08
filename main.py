from re import sub
f=lambda x:sorted(sub(r'[ .,\-!?;:]','',x.lower()))
print(['NO','YES'][f(input())==f(input())])