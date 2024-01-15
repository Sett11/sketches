a,b,c,d=input(),input(),input(),input()
o,w={a[i]:b[i] for i in range(len(a))},{b[i]:a[i] for i in range(len(a))}
print(''.join(o[i] for i in c),''.join(w[i] for i in d),sep='\n')