# threading Пример разделения выполнения программы на разные потоки

import random
import time
import threading

def f(n):
    sec=random.randrange(1,10)
    time.sleep(sec)
    print(f'I am Worker {n}, i slept for {sec} seconds')

# синхронная версия
# for i in range(5):
#     f(i)

# мультипоточная версия
# for i in range(5):
#     t=threading.Thread(target=f,args=(i,))
#     t.start()

print('All Threads finiched???')