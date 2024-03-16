from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import time
import requests

# функция g делает запрос, функция f принимает флаг (по дефолту - False) и 30 раз вызывает функцию g
# в случае флага - False синхронно, в противоположном случае - через pool executor (абстракция над процессами и тредами)

def g():
    params={'q':'fack'}
    response=requests.get('http://google.com/search',params=params)
    print(response.status_code)

def f(flag=False):
    if not flag:
        for _ in range(30):
            g()
    else:
        ex=ThreadPoolExecutor()
        for _ in range(30):
            ex.submit(g)
        ex.shutdown(wait=True)

if __name__=='__main__':
    t=time.time()
    f(True)
    print(time.time()-t)