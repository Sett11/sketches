s=input()
print(['NO','YES'][all(i in s for i in ['.','@'])])