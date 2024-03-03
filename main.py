s = input()
def both_ends(s):
    return s[:2]+s[-2:] if len(s)>1 else ''

print(both_ends(s))