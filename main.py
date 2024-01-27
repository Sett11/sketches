from collections import deque

def f(s):
    q=deque()
    for i in s:
        if i=='(':
            q.append(i)
        else:
            if not q or q.pop()+i!='()':
                return 1==2
    return not q

print(f(input()))