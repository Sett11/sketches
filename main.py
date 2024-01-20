from xml.etree.ElementTree import XMLParser

class C:
    o={'d':0,'red':0,'green':0,'blue':0}
    def start(self,tag,attr):
        self.o['d']+=1
        self.o[attr['color']]+=self.o['d']
    def end(self,tag):
        self.o['d']-=1
    def data(self,data):
        pass
    def close(self):
        return f"{self.o['red']} {self.o['green']} {self.o['blue']}"
t=C()
p=XMLParser(target=t)
p.feed(input())
print(p.close())