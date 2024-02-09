from random import randint as r
from string import ascii_uppercase as a
generate_index=lambda:'{0}{1}{2}_{2}{1}{0}'.format(a[r(0,25)],a[r(0,25)],r(0,99))

print(generate_index())