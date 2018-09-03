import subprocess
import cv2
import time
from imutils.video import VideoStream
from threading import Thread, Event
from fps import Fps
from utils import thread_callback

class OpencvVideoSource(object):
    def __init__(self, video_device_id=-1, use_thread=True, limit_frame_rate = False, resolution = None):
        self.video_device_id = video_device_id
        self.limit_frame_rate = limit_frame_rate
        self.resolution = resolution
        self.use_thread = use_thread
        self._image = None
        self.last_image_read = True # whether last frame has been used
        self.fps = Fps()
        self.fps.start()
        self.event = Event()

    def start_camera(self):
        start = time.time()
        self.cap = cv2.VideoCapture(self.video_device_id)
        self.cap.set(cv2.cv.CV_CAP_PROP_FPS, 20)
        print('>>> opened VideoCapture (%s) in %.3f seconds' % (self.video_device_id, time.time() - start))
        # subprocess.check_output(['bash', '-c', 'v4l2-ctl -c backlight_compensation=1,sharpness=130,power_line_frequency=1,white_balance_temperature_auto=1,saturation=128,contrast=128,brightness=128,focus_absolute=0,focus_auto=0'])
        self.running = True
        if self.use_thread:
            start = time.time()
            self.thread = Thread(target = thread_callback(self.grab_frames), args=())
            self.thread.daemon = True
            self.thread.start()
            print('>>> camera thread started in %.3f seconds' % (time.time() - start))

        return self

    def stop_camera(self):
        self.running = False

    def grab_frames(self):
        while self.running:
            self.fps.update()
            self._image = self.grab_frame()
            self.last_image_read = False
            # time.sleep(0.02) # useful when reading video from file
            if self.limit_frame_rate:
                self.event.wait()
                self.event.clear()

    def grab_frame(self):
        ret, frame = self.cap.read()
        if self.resolution is not None and frame is not None:
            frame = cv2.resize(frame, self.resolution)
        return frame

    def get_rgb_image(self):
        if self.get_image() is None:
            return None
        return cv2.cvtColor(self.get_image(), cv2.COLOR_BGR2RGB)

    def get_rgb_bgr_image(self):
        bgr_image = self.get_image()
        if bgr_image is None:
            return (None, None)
        return (cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB), bgr_image)

    def get_bgr_image(self):
        return self.get_image()

    def get_image(self):
        if not self.use_thread:
            self._image = self.grab_frame()
            self.fps.update()
        # if self._image is None:
        #     return None
        # small = cv2.resize(self._image, (0,0), fx=0.5, fy=0.5)
        self.last_image_read = True
        if self.limit_frame_rate:
            self.event.set() # continue grabbing next frame
        return self._image

class ImutilsVideoSource(object):
    def __init__(self, video_device_id=-1, use_thread=True):
        self.video_device_id = video_device_id
        self._image = None
        self.use_thread = use_thread
        self.fps = Fps()
        self.fps.start()

    def start_camera(self):
        start = time.time()
        self.video_stream = VideoStream(src=self.video_device_id).start()
        print('>>> opened VideoCapture in %.3f seconds' % (time.time() - start))
        # subprocess.check_output(['bash', '-c', 'v4l2-ctl -c backlight_compensation=1,sharpness=130,power_line_frequency=1,white_balance_temperature_auto=1,saturation=128,contrast=128,brightness=128,focus_absolute=0,focus_auto=0'])
        self.running = True
        if self.use_thread:
            start = time.time()
            self.thread = Thread(target = thread_callback(self.grab_frames), args=())
            self.thread.daemon = True
            self.thread.start()
            print('>>> camera thread started in %.3f seconds' % (time.time() - start))

        return self

    def stop_camera(self):
        self.running = False

    def grab_frames(self):
        while self.running:
            self.fps.update()
            self._image = self.video_stream.read()

    def get_rgb_image(self):
        if self.get_image() is None:
            return None
        return cv2.cvtColor(self.get_image(), cv2.COLOR_BGR2RGB)

    def get_rgb_bgr_image(self):
        bgr_image = self.get_image()
        if bgr_image is None:
            return (None, None)
        return (cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB), bgr_image)

    def get_bgr_image(self):
        return self.get_image()

    def get_image(self):
        if not self.use_thread:
            ret, self._image = self.video_stream.read()
            self.fps.update()
        # if self._image is None:
        #     return None
        # small = cv2.resize(self._image, (0,0), fx=0.5, fy=0.5)
        return self._image
