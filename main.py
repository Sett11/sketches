func=lambda s:len(set((s[0]+s[-1]).lower()))==1 and s[0] in 'Aa'

print(func('Abbba'))