import datetime

print(*map(int,str(datetime.date(*map(int,input().split()))+datetime.timedelta(int(input()))).split('-')))