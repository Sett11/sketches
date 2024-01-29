a=list(map(int,input().split()))
print(*sum([[a[i],a[i-1]] for i in range(1,len(a),2)]+([[a[-1]]] if len(a)&1 else []),[]))