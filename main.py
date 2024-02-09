from random import shuffle as h
matrix = [[1, 2, 3, 4],
          [5, 6, 7, 8],
          [9, 10, 11, 12],
          [13, 14, 15, 16]]
h(list(map(lambda x:h(x),matrix)))
print(matrix)