t=0
with open('ledger.txt') as f:
    for i in f:
        t+=int(i[1:].strip())
print(f'${t}')