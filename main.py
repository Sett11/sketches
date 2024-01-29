d={"Первая четверть": 0,
"Вторая четверть": 0,
"Третья четверть": 0,
"Четвертая четверть": 0}

for x,y in [list(map(int,input().split())) for i in range(int(input()))]:
    if x>0 and y>0:
        d["Первая четверть"]+=1
    elif x<0 and y>0:
        d["Вторая четверть"]+=1
    elif x<0 and y<0:
        d["Третья четверть"]+=1
    elif x>0 and y<0:
        d["Четвертая четверть"]+=1

for i in d:
    print(f'{i}: {d[i]}')