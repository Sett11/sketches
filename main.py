class NonPositiveError(Exception):
    pass

class PositiveList(list):
    def append(self,x):
        if x>0:
            self+=[x]
        else:
            raise NonPositiveError()

p=PositiveList()
p.append(1)
p.append(-1)