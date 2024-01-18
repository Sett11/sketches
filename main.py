class multifilter:
    def judge_half(pos,neg):
        return pos>=neg

    def judge_any(pos,neg):
        return pos

    def judge_all(pos,neg):
        return not neg

    def __init__(self, iterable, *funcs, judge=judge_any):
        self.iterable=iterable
        self.funcs=funcs
        self.judge=judge

    def __iter__(self):
        r=[]
        for i in self.iterable:
            t=[j(i) for j in self.funcs]
            if self.judge(t.count(True),t.count(False)):
                r.append(i)
        return (i for i in r)

def mul2(x):
    return x % 2 == 0

def mul3(x):
    return x % 3 == 0

def mul5(x):
    return x % 5 == 0

a = [i for i in range(31)]

print(list(multifilter(a, mul2, mul3, mul5,judge=multifilter.judge_all))) 