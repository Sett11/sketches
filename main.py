n = 4
count = 0
maximum = -10e9
for i in range(n):
    x = int(input())
    if x&1:
        count += 1
        if x > maximum:
            maximum = x
if count > 0:
    print(count)
    print(maximum)
else:
    print('NO')