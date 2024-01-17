class ExtendedStack(list):
    def sum(self):
        self.append(self.pop()+self.pop())
    def sub(self):
        self.append(self.pop()-self.pop())
    def mul(self):
        self.append(self.pop()*self.pop())
    def div(self):
        self.append(self.pop()//self.pop())

a=ExtendedStack()
a.append(1)
a.extend([2,3,4])
print(a)
a.mul()
print(a)