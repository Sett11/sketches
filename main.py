s=input()
a,b=s.find('h'),s.rfind('h')
print(s[:a+1]+s[a+1:b][::-1]+s[b:])