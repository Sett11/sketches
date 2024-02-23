from random import randint
with open('random.txt','w',encoding='utf-8') as f:
    for i in range(25):
        f.write(str(randint(111,777))+'\n')