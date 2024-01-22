a,b=sorted([[int(input()),int(input())],[int(input()),int(input())]])
print(*set([max(a[0],b[0]),min(a[1],b[1])])) if min(b)<=max(a) else print('пустое множество')