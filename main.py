n=int(input())
print(*[f"Квадрат числа {i} равен {i**2}" for i in range(n+1)],sep='\n')