a,b,c=10,5,.5
for i in range(1,11):
    for j in range(1,21):
        for k in range(1,201):
            if i*a+j*b+k*c==100 and i+j+k==100:
                print(i,j,k)