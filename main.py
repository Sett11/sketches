s=input()
print(['NO','YES'][s==''.join(sorted(s,reverse=True))])