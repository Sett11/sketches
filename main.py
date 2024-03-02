s=input()
if s in ['list','str','int']:
    if s=='int':
        a,b=int(input()),int(input())
        if not a and not b:
            print("Empty Ints")
        else:
            print(a+b)
    elif s=='str':
        c=input()
        print(c or "Empty String")
    else:
        a=input().split()
        print(a[-1] if a else "Empty List")
else:
    print("Unknown type")