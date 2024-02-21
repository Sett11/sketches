is_non_negative_num=lambda s:bool(__import__('re').match(r'^\d*\.?\d*?$',s))

print(is_non_negative_num('0'))