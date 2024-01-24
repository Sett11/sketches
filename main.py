for i in range(1,151):
    for j in range(i,151):
        for k in range(j,151):
            for h in range(k,151):
                for n in range(h,151):
                    x=int(i**5)+int(j**5)+int(k**5)+int(h**5)
                    if x==int(n**5):
                        print(i+j+k+h+n)
                        break
                    if n**5>x:
                        break

