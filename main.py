from random import randint
generate_ip=lambda:'.'.join(str(randint(0,255)) for _ in range(4))

print(generate_ip())