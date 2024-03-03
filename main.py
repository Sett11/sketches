n=int(input())
donuts=lambda n:f'Всего пончиков: {n if n<10 else "много"}'
print(donuts(n))