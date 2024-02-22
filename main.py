def generate_letter(mail, name, date, time, place,teacher='Тимур Гуев',number=17):
    return """To: {0}
    Приветствую, {1}!
    Вам назначен экзамен, который пройдет {2}, в {3}.
    По адресу: {4}. 
    Экзамен будет проводить {5} в кабинете {6}. 
    Желаем удачи на экзамене!""".format(mail, name, date, time, place,teacher,number)

print(generate_letter(1,2,3,4,5))