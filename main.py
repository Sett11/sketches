with open('numbers.txt', encoding='utf-8') as file:
    for i in file:
        print(sum(map(int,i.split())))
        