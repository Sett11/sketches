def print_fio(a, b, c):
    return (b[0]+a[0]+c[0]).upper()

name, surname, patronymic = input(), input(), input()
print(print_fio(name, surname, patronymic))