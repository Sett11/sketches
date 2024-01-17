import time

class Loggable:
    def log(self, msg):
        print(str(time.ctime()) + ": " + str(msg))

class LoggableList(list,Loggable):
    def append(self,x):
        self+=[x]
        super(LoggableList,self).log(x)
        
l=LoggableList()
l.append(1)
l.append(7)
print(l)