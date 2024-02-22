f=open('prices.txt')
print(sum(map(lambda s:int(s.split('\t')[-1])*int(s.split('\t')[-2]),f.readlines())))
f.close()