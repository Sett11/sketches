def info_kwargs(**kwargs):
    print(*map(lambda s:f'{s[0]}: {s[1]}',sorted(kwargs.items())),sep='\n')

info_kwargs(first_name='Timur', last_name='Guev', age=28, job='teacher')