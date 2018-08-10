import time
import cv2
from known_face_detector import KnownFaceDetector
from face_detector import *
from video_source import *
from fps import Fps
from display import DisplayWindow
from data import Dataset, DataUpdater
from model import Model
from tracker import Tracker
from utils import *
from messenger import MqttMessenger

print(">>> Starting in %s environment" % (current_env()))

# video_device can be fully qualified uri pointing to a video stream/file or a simple video file path
# video_device can be a number identifying the camera device or -1 for default camera
video_device = env_variable('video_device', -1)
enable_display = env_variable('enable_display', 'False').lower() == "true"
state_file_path = env_variable('state_file', '/data/people_identifier.json')
verbose_logging = env_variable('debug', 'True').lower() == "true"

# [LEARNING]: OpencvVideoSource seems slightly faster
camera = OpencvVideoSource(video_device_id=video_device, use_thread=True, limit_frame_rate=False, resolution=(640, 480)).start_camera()
# camera = ImutilsVideoSource(video_device_id=-1, use_thread=True).start_camera()

dataset = Dataset(state_file_path)
model = Model(dataset)

detector = KnownFaceDetector(model, face_detector_class=DlibFaceDetector)
# detector = KnownFaceDetector(model, face_detector_class=OpencvDnnFaceDetector)

messenger = MqttMessenger()
tracker = Tracker(messenger)
updater = DataUpdater(dataset, messenger, lambda : camera.get_rgb_bgr_image()[0])
fps = Fps()
if enable_display:
    display = DisplayWindow()

fps.start()
updater.listen()

not_ready_printed=False
frame_number = 0


while True:
# while fps.elapsed()<15:
    frame_number = frame_number + 1
    (img, bgr_image) = camera.get_rgb_bgr_image()
    if img is None:
        if not not_ready_printed:
            not_ready_printed=True
            print("image not available yet")
        continue

    if not_ready_printed:
        not_ready_printed = False
        print("camera now ready")
    # cv2.imwrite('./%04d.png' % frame_number, img)

    detected_faces = detector.identify_faces(img,100)
    tracker.update(detected_faces)
    if enable_display:
        display.show(bgr_image, detected_faces)
    # print(detected_faces)
    fps.update()
    if frame_number % 10 == 0 and verbose_logging:
        print("program: " + fps.info())
        print("Camera: " + camera.fps.info())
    # time.sleep(0.01)
