class MoneyBox:
    def __init__(self,size):
        self.size=size
        self.count=0

    def can_add(self,v):
        return self.count+v<=self.size

    def add(self,v):
        self.count+=v