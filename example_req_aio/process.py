# Примечание - в случае использования процессов способ запуска является принципиальным, иначе приводит к неблокирующей ошибке

import random
import time
import os
import multiprocessing
from statistics import mean


# пример распараллеливания вычислительной задачи
# представлена функция, вычисляющая n-е число Фибоначчи
# в первом примере её применения сначала вычисляется значение первого вызова функции, после этого второе
# во втором примере вычисление происходит конкурентно в разных процессах


def fib(n):
    return 0 if n==0 else 1 if n==1 else fib(n-1)+fib(n-2)

# def ff():
#     fib(33)
#     fib(34)

# times=[]

# for _ in range(5):
#     t=time.time()
#     ff()
#     times.append(time.time()-t)

# print(mean(times))

# if __name__=='__main__':
#     def f():
#         x=multiprocessing.Process(target=fib,args=(33,))
#         y=multiprocessing.Process(target=fib,args=(34,))
#         x.start()
#         y.start()
#         x.join()
#         y.join()

#     times=[]
#     for _ in range(5):
#         t=time.time()
#         f()
#         times.append(time.time()-t)
#     print(mean(times))

# создаётся функция, которая печатает идентификатор текущего процесса, затем она передаётся в класс Process модуля multiprocessing,
# затем печатается идентификатор родительского процесса и затем главный процесс закрывается

# def hello():
#     print(f'Привет от дочернего процесса {os.getpid()}')

# if __name__=='__main__':
#     P=multiprocessing.Process(target=hello)
#     P.start()
#     print(f'Привет от родительского процесса {os.getpid()}')
#     P.join()



# def f(n):
#     s = random.randrange(1,10)
#     time.sleep(s)
#     print(f"I am Worker {n}, i slept for {s} seconds")

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