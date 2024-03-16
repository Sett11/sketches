import random
import time
import threading
from statistics import mean

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

# def f():
#     x=threading.Thread(target=fib,args=(33,))
#     y=threading.Thread(target=fib,args=(34,))
#     x.start()
#     y.start()
#     x.join()
#     y.join()

# times=[]
# for _ in range(5):
#     t=time.time()
#     f()
#     times.append(time.time()-t)
# print(mean(times))


# получаем количество активных потоков и имя актуального потока
# print(threading.active_count(),threading.current_thread().name)

# создаются функции, которые печатают актуальный поток, они передаются в класс Thread модуля threading, затем запускается главный поток и 
# печатается количество активных потоков и имя актуального потока, затем главный поток закрывается

# def hello():
#     print(f'Привет от потока {threading.current_thread()}')

# def fack():
#     print(f'Fack you from thread {threading.current_thread()}')

# hell=threading.Thread(target=hello)
# hell2=threading.Thread(target=fack)

# hell.start()
# hell2.start()

# print(f'В настоящий момент выполняется {threading.active_count()} потоков',f'Имя текущего {threading.current_thread().name}',sep='\n')
# hell.join()
# hell2.join()


# def f(n):
#     sec=random.randrange(1,10)
#     time.sleep(sec)
#     print(f'I am Worker {n}, i slept for {sec} seconds')

# x=time.time()

# f(1),f(2),f(3)


# t,p,r=threading.Thread(target=f,args=(1,)),threading.Thread(target=f,args=(2,)),threading.Thread(target=f,args=(3,))
# t.start(),p.start(),r.start()
# t.join(),p.join(),r.join()

# print('All Threads finiched???',time.time()-x,sep='\n')