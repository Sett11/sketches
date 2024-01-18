with open('dataset_24465_4.txt') as r,open('b.txt','a') as a:
    s=r.read().splitlines()
    for i in s[::-1]:
        a.write(i+'\n')