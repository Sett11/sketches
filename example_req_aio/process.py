# multiprocessing Пример разделения выполнения программы на разные процессы (если количество ядер позволяет)
# Примечание - в случае использования процессов способ запуска является принципиальным, иначе приводит к неблокирующей ошибке
# В нашем случае работает не вполне корректно, возможно ввиду малого количества ядер.

import random
import time
import multiprocessing 

def f(n):
    s = random.randrange(1,10)
    time.sleep(s)
    print(f"I am Worker {n}, i slept for {s} seconds")

# if __name__=='__main__':
# 
#     for i in range(2):
#         f(i)
    
#     print("All Processes are queued, let's see when they finish!")

# if __name__=='__main__':

#     for i in range(2):
#         t = multiprocessing.Process(target=f,args=(i,))
#         t.start()
#         t.join()

#     print("All Processes are queued, let's see when they finish!")