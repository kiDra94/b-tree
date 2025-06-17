import time

class Node:
    def __init__(self, value, left, right):
        self.value = value
        self.left = left
        self.right = right

    def dump(self, indent=""):
        print(indent + self.value)
        if self.left is not None:
            self.left.dump(indent + "  ")
        if self.right is not None:
            self.right.dump(indent + "  ")


class Hdd:
    def __init__(self, sectors, rings):
        self.data = [[0] * sectors for _ in range(rings)]

    def get(self, sector, ring):
        return self.data[sector][ring]

class Ram:
    def __init__(self, size):
        self.data = [0] * size

    def load(self, hdd, ring, sector, address):
        print("Loading data")
        time.sleep(2)
        self.data[address] = hdd.get(ring, sector)
        print(f"Data at address: {self.data[address]} loaded\nFineshed loading!")
    

bm = Node("bm", None, None)
sg = Node("sg", None, None)
hm = Node("hm", None, None)
fe = Node("fe", None, None)

akku = Node("Akku", bm, sg)
man = Node("Man", hm, fe)

werkzeug = Node("Werkzeug", akku, man)
werkzeug.dump()

hdd = Hdd(3, 5)
ram = Ram(5)
ram.load(hdd, 2, 1, 0)
