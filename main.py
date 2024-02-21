is_num=lambda s:bool(__import__('re').match(r'^\-?\d*\.?\d*?$',s))

print(is_num('-10'))