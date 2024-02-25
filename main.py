filename = input()
with open(filename, encoding='utf-8') as file:
    content = file.readlines()
    count = len(content)
    if count < 10:
        for s in content:
            print(s, end='')
    else:
        res = content[-10:]
        for s in res:
            print(s, end='')