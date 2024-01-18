from simplecrypt import decrypt, encrypt

with open('encrypted.bin', 'rb') as inp:
    encrypted = inp.read()
    with open('passwords.txt', 'r') as passwd:
        for line in passwd:
            try:
                output = decrypt(line.strip(), encrypted)
            except Exception:
                print(line.strip(), " - неправильный пароль")
            else:
                print(line.strip(), '- правильный пароль. Текст:', output.decode('utf8'))