# 6 Пример синхронного (последовательного) выполнения программы

import time
import asyncio

# def f1(n):
#     print('f1 start')
#     print(n**2)
#     time.sleep(3)
#     print('f1 comleted')

# def f2(n):
#     print('f2 start')
#     print(n**.5)
#     time.sleep(3)
#     print('f2 comleted')

# def main():
#     print('Start main')
#     f1(5)
#     f2(5)
#     print('Comleted main')

# print(time.strftime('%X'))
# main()
# print(time.strftime('%X'))

# Пример асинхронного (непоследовательного) выполнения программы
# async def f1(n):
#     print('f1 start')
#     print(n**2)
#     await asyncio.sleep(3)
#     print('f1 comleted')

# async def f2(n):
#     print('f2 start')
#     print(n**.5)
#     await asyncio.sleep(3)
#     print('f2 comleted')

# async def main():
#     print('Start main')
#     a=asyncio.create_task(f1(5))
#     b=asyncio.create_task(f2(5))
#     await a, await b
#     print('Comleted main')

# print(time.strftime('%X'))
# asyncio.run(main())
# print(time.strftime('%X'))