from known_face_detector import KnownFaceDetector
from face_detector import *
from video_source import *
from fps import Fps
from display import DisplayWindow
from data import Dataset
from model import Model
from tracker import Tracker
from utils import *
import time
import cv2

# [LEARNING]: OpencvVideoSource seems slightly faster
camera = OpencvVideoSource(video_device_id=-1, use_thread=True, limit_frame_rate=True, resolution=(640, 480)).start_camera()
# camera = OpencvVideoSource(video_device_id="./video.webm", use_thread=True, limit_frame_rate=True, resolution=(640, 480)).start_camera()
# camera = ImutilsVideoSource(video_device_id=-1, use_thread=True).start_camera()

dataset = Dataset('./people_identifier.pkl')
model = Model(dataset)

detector = KnownFaceDetector(model, face_detector_class=DlibFaceDetector)
# detector = KnownFaceDetector(model, face_detector_class=OpencvDnnFaceDetector)

messenger = MqttMessenger()
tracker = Tracker(messenger)
display = DisplayWindow()
fps = Fps()

fps.start()

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
    # if len(detected_faces) > 0:
    #     for detection in detected_faces:
    #         publish_message(detection["class"], detection)
    # else:
    #     # print("no faces detected")
    #     pass
    fps.update()
    print("program: " + fps.info())
    print("Camera: " + camera.fps.info())
    display.show(bgr_image, detected_faces)
    time.sleep(0.01)
