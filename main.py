s=input()
print(['NO','YES'][len(s)>6 and any(i.isdigit() for i in s) and any(i.islower() for i in s) and any(i.isupper() for i in s)])