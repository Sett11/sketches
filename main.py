a, b = input(), input()


def f(a, b):
    if b not in a:
        return 0
    r, i = 0, a.find(b)
    while i != -1:
        i = a.find(b, i + 1)
        r += 1
    return r


print(f(a, b))
