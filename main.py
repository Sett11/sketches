with open('words.txt') as f:
    a=sorted(f.read().replace('\n',' ').split(),key=len,reverse=True)
    print(*[i for i in a if len(i)==len(a[0])],sep='\n')