from detector.known_face_detector import KnownFaceDetector
from opencv_video_source import OpencvVideoSource
import time
import cv2

# print(type(KnownFaceDetector))
detector = KnownFaceDetector()
# print(detector)


# import cv2
# cap = cv2.VideoCapture(0)
camera = OpencvVideoSource(0).start_camera()

fps_over_frames=50

global_start = time.time()
frame_times=[global_start]
frame = 0
while True:
    # ret, bgrImg = cap.read()
    # rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    img = camera.get_image()
    if img is None:
        print("image not available yet")
        continue
    # cv2.imwrite('./%04d.png' % frame, img)
    # faces = detector.detect_faces(img)
    # if len(faces) > 0:
    #     # raise event saying some face detected and if it is known face or not
    #     print("detected %d faces" % len(faces))
    #     print(faces)
    #     pass
    frame = frame + 1
    frame_times.append(time.time())
    frame_times = frame_times[-fps_over_frames:]
    elapsed = frame_times[-1] - global_start
    fps = (len(frame_times) - 1.0) / (frame_times[-1] - frame_times[0])
    print("frame: %4d \t fps (last %d frames): %2.3f \t elapsed: %2.2f sec" % (frame, len(frame_times), fps, elapsed))

