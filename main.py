import os

x=input()
if os.path.exists(x):
    if os.path.isfile(x):
        with open(x,'r',encoding='utf-8') as f:
            print(f'CONTENT:\n{f.read()}')
    else:
        print('ERROR:\nЭто каталог, а не файл')
else:  
    print('ERROR:\nФайл не существует')