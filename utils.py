import pickle
import os
import json

def load_file(filename, extension='pkl'):
    with open(filename+"."+extension, 'rb') as file_handle:
        result = pickle.load(file_handle)
    return result

def save_file(data, filename, extension='pkl'):
    with open(filename+"."+extension, 'wb') as file_handle:
        pickle.dump(data, file_handle)

def exists(filename, extension = "pkl"):
    return os.path.exists(filename+"."+extension)


class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Rectangle(list):
    """ A rectangle with useful methods """
    def __init__(self, x1, y1, x2, y2):
        if(x1>x2):
            (x1,x2) = (x2,x1)
        if(y1>y2):
            (y1,y2) = (y2,y1)
        list.__init__([x1,y1,x2,y2])
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def left(self):
        return self.x1
    def top(self):
        return self.y1
    def right(self):
        return self.x2
    def bottom(self):
        return self.y2

    def width(self):
        return self.x2-self.x1

    def height(self):
        return self.y2-self.y1

    def area(self):
        return self.width*self.height

    def toJSON(self):
        return json.dumps([x1,y1,x2,y2])
