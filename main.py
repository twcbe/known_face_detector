from known_face_detector import KnownFaceDetector
from opencv_video_source import OpencvVideoSource
from fps import Fps
from utils import *
import time
import cv2

fps = Fps()

detector = KnownFaceDetector()
camera = OpencvVideoSource(video_device_id=0, use_thread=False).start_camera()
fps.start()
not_ready_printed=False
frame_number = 0
while True:
    frame_number = frame_number + 1
    img = camera.get_rgb_image()
    if img is None:
        if not not_ready_printed:
            not_ready_printed=True
            print("image not available yet")
        continue

    if not_ready_printed:
        not_ready_printed = False
        print("camera now ready")
    # cv2.imwrite('./%04d.png' % frame_number, img)

    faces = detector.detect_faces(img,100)
    if len(faces) > 0:
        # cv2.imwrite('./%04d.png' % frame_number, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        # raise event saying some face detected and if it is known face or not
        print("detected %d faces" % len(faces))
        print(faces)
    else:
        print("no faces detected")
    fps.update()
    print("program: " + fps.info())
    print("Camera: " + camera.fps.info())
    time.sleep(0.01)
