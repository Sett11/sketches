n=int(input())
print(['NO','YES'][(n%4==0 and n%100!=0) or (n%400==0)])