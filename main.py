from decimal import *
d = Decimal(input())
def e(num):
    return num.exp()
def sqrt(num):
    return num.sqrt()
def ln(num):
    return num.ln()
def lg(num):
    return num.log10()
print(e(d) + ln(d) + lg(d) + sqrt(d))