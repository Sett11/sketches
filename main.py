s=input()
print(int((s[0] if len(s)==6 else '')+s[-5:][::-1]))