s=input()
print('NO' if 'f' not in s else s.find('f') if s.count('f')==1 else ' '.join([str(s.find('f')),str(s.rfind('f'))]))