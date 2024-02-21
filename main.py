n=int(input())
print({'квадрат':lambda x:x**2,'корень':lambda x:x**.5,'куб':lambda x:x**3,'модуль':abs,'синус':__import__('math').sin}[input()](n))