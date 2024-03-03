front_x=lambda a:sorted(a,key=lambda x:(not x.startswith('x'),x))

print(front_x(['mix', 'extra', '', 'x-files', 'xyz', 'xapple', 'apple']))