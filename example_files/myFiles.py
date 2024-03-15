import os
from generate_random_text import rand_list

# 1
# f=open('exampleFiles\\text.txt','r')
# print(f.read())
# f.close()

# 2
# with open('exampleFiles\\text.txt','r') as f:
#     print(f.read())

# 3
# with open('exampleFiles\\text.txt','r') as f:
#     s=f.readline()
#     while s:
#         print(s.rstrip())
#         s=f.readline()

# 4
# with open('exampleFiles\\text.txt','r') as f:
#     for i in f.readlines():
#         print(i.rstrip())

# 5
# with open('exampleFiles\\text1.txt','w') as f:
#     f.write('111\n222\n333')

# 6
# with open('exampleFiles\\text1.txt','w') as f:
#     f.writelines(map(lambda s:s+'\n',rand_list))

# 7
# with open('main.py','r') as func, open('exampleFiles\\new_my.py','w') as f:
#     print(f.write(func.read()))

# 8
# with open('text1.txt','w',encoding='utf-8') as f:
#     for i in range(1,int(input())+1):
#         f.write(f'{i}: {input()}\n')
#     print(f.fileno(),f.isatty(),sep='\n')

# 9
# print(os.getcwd())
# print(os.getcwdb())
# print(os.listdir('.'))

# 10
# for dir_path,dir_names,file_names in os.walk('.'):
#     for dir_name in dir_names:
#         print('DIR: ',dir_name)
#     for file_name in file_names:
#         print('FILE: ',file_name)

# 11
# print(os.path.abspath('myFiles.py'))
# print(os.path.getatime('exampleFiles\\myFiles.py'))