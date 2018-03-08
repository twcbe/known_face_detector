import pickle

def load_file(filename, extension='pkl'):
    with open(filename+"."+extension, 'rb') as file_handle:
        result = pickle.load(file_handle)
    return result

def save_file(data, filename, extension='pkl'):
    with open(filename+"."+extension, 'rb') as file_handle:
        pickle.dump(data, file_handle)

class Rectangle(object):
    """ A rectangle with useful methods """
    def __init__(self, x1, y1, x2, y2):
        if(x1>x2):
            (x1,x2) = (x2,x1)
        if(y1>y2):
            (y1,y2) = (y2,y1)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def left():
        return self.x1
    def top():
        return self.y1
    def right():
        return self.x2
    def bottom():
        return self.y2

    def width():
        return self.x2-self.x1

    def height():
        return self.y2-self.y1

    def area():
        return self.width*self.height
