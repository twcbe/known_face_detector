import os
import json
import cv2
import numpy as np
import os
import traceback
import thread

def load_env_config():
    environment = current_env()
    with open("config/settings/%s.json" % environment) as f:
        global settings
        settings = json.load(f)

def current_env():
    return env_variable('ENV', 'development')

def env_variable(key, default = None):
    return os.environ.get(key) or default

def get_settings():
    global settings
    return settings

def load_file(filename):
    if not exists(filename):
        return None

    with open(filename, 'rb') as file_handle:
        result = json.load(file_handle)
    return result

def save_file(data, filename):
    with open(filename, 'wb') as file_handle:
        json.dump(data, file_handle)

def exists(filename):
    return os.path.exists(filename)


def base64_to_image(encoded_data):
    if encoded_data is None:
        return None
    nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def rgb2bgr(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

def bgr2rgb(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def filter_keys(dictionary, keys):
    return dict((key, dictionary[key]) for key in keys)

def thread_callback(thread_callback_fn):
    def callback():
        try:
            thread_callback_fn()
        except:
            traceback.print_exc()
            thread.interrupt_main()
    return callback

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

load_env_config()
