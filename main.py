s = input()
def fix_start(s):
    a,b=s[0],s[1:]
    return a+b.replace(a,'*')

print(fix_start(s))