def number_system():
    return [a for a in range(10) if 8 * a ** 1 + 8 * a **0  == ((3 * a ** 1) + (2 * a ** 0)) + ((2 * a ** 1) + (2 * a ** 0)) + ((1 * a ** 1) + (6 * a ** 0)) + ((1 * a ** 1) + (7 * a ** 0))]
                                                                                                                                       
print(number_system())