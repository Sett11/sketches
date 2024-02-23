from re import split
with open('nums.txt', encoding='utf-8') as file:
    print(sum([int(i) for i in split(r'[^\d]',file.read()) if i.isdigit()]))
        