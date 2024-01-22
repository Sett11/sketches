a,b,c=sorted(map(lambda x:len(x),[input(),input(),input()]))
print(['NO','YES'][c-b==b-a])