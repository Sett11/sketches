# threading Пример разделения выполнения программы на разные потоки

import random
import time
import threading

def f(n):
    sec=random.randrange(1,10)
    time.sleep(sec)
    print(f'I am Worker {n}, i slept for {sec} seconds')

x=time.time()

# f(1),f(2),f(3)


# t,p,r=threading.Thread(target=f,args=(1,)),threading.Thread(target=f,args=(2,)),threading.Thread(target=f,args=(3,))
# t.start(),p.start(),r.start()
# t.join(),p.join(),r.join()

print('All Threads finiched???',time.time()-x,sep='\n')