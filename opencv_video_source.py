import subprocess
import cv2
import time
from threading import Thread
from fps import Fps

class OpencvVideoSource(object):
    def __init__(self, video_device_id=0):
        self.video_device_id = video_device_id
        self.image = None

    def start_camera(self):
        start = time.time()
        self.cap = cv2.VideoCapture(self.video_device_id)
        print('>>> opened VideoCapture in %.3f seconds' % (time.time() - start))
        # subprocess.check_output(['bash', '-c', 'v4l2-ctl -c backlight_compensation=1,sharpness=130,power_line_frequency=1,white_balance_temperature_auto=1,saturation=128,contrast=128,brightness=128,focus_absolute=0,focus_auto=0'])
        self.running = True
        start = time.time()
        self.thread = Thread(target = self.grab_frames, args=())
        self.thread.daemon = True
        self.thread.start()
        print('>>> camera thread started in %.3f seconds' % (time.time() - start))

        return self

    def stop_camera(self):
        self.running = False

    def grab_frames(self):
        self.fps = Fps()
        self.fps.start()
        while self.running:
            self.fps.update()
            ret, self.image = self.cap.read()

    def get_rgb_image(self):
        if self.get_image() is None:
            return None
        return cv2.cvtColor(self.get_image(), cv2.COLOR_BGR2RGB)

    def get_bgr_image(self):
        return self.get_image()

    def get_image(self):
        if self.image is None:
            return None
        # small = cv2.resize(self.image, (0,0), fx=0.5, fy=0.5)
        return self.image
