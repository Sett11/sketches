# multiprocessing Пример разделения выполнения программы на разные процессы (если количество ядер позволяет)
# Примечание - в случае использования процессов способ запуска является принципиальным, иначе приводит к неблокирующей ошибке

import random
import time
import multiprocessing 

def f(n):
    s = random.randrange(1,10)
    time.sleep(s)
    print(f"I am Worker {n}, i slept for {s} seconds")

# if __name__=='__main__':
#     x=time.time()
#     f(1)
#     f(2)
#     print("All Processes are queued, let's see when they finish!",time.time()-x,sep='\n')

# if __name__=='__main__':
#     x=time.time()
#     t=multiprocessing.Process(target=f,args=(1,))
#     p=multiprocessing.Process(target=f,args=(2,))
#     t.start()
#     p.start()
#     t.join()
#     p.join()
#     print("All Processes are queued, let's see when they finish!",time.time()-x,sep='\n')