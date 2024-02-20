def print_products(*args):
    a=[f'{i+1}) {j}' for i,j in enumerate([k for k in args if k and isinstance(k,str)])]
    print(*a if a else 'Нет продуктов',sep='\n' if a else '')

print_products('Бананы', [1, 2], ('Stepik',), 'Яблоки', '', 'Макароны', 5, True)
print_products([4], {}, 1, 2, {'Beegeek'}, '') 