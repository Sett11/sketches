def pretty_print(a,side='-',delimiter='|'):
    z=f'{delimiter} '+f' {delimiter} '.join(map(str,a))+f' {delimiter}'
    c=' '+f'{side}'*(len(z)-2)+'\n'
    print((c+z+'\n'+c).rstrip('\n'))

print(pretty_print(['abc', 'def', 'ghi'], side='*', delimiter='#'))