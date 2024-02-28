from string import ascii_letters,digits
from random import randint,sample,shuffle

def generate_random_list():
    a=list(ascii_letters+digits)
    shuffle(a)
    return [''.join(sample(a,randint(1,20))) for _ in range(randint(1,20))]

rand_list=generate_random_list()