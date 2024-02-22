def concat(*args,sep=' '):
    return f'{sep}'.join(map(str,args))

print(concat('hello', 'python', 'and', 'stepik',sep='*'))