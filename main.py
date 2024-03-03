def kaprekar_step(L):
    L.sort()
    return int(''.join(map(str,L[::-1])))-int(''.join(map(str,L)))

print(kaprekar_step([4, 5, 6, 8]))