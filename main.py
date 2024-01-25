c=0

for i in range(int(input())):
    if input().count('11')>=3:
        c+=1

print(c)