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

print('>>> Starting in %s environment' % (current_env()))

# video_device can be fully qualified uri pointing to a video stream/file or a simple video file path
# video_device can be a number identifying the camera device or -1 for default camera
video_device                            = env_variable('video_device',             "-1")
enable_display                          = env_variable('enable_display',           'False', bool)
enable_events                           = env_variable('enable_events',            'False', bool)
verbose_logging                         = env_variable('debug',                    'True',  bool)
limit_frame_rate                        = env_variable('limit_frame_rate',         'False', bool)
state_file_path                         = env_variable('state_file',               '/data/people_identifier.json')
training_samples_file_path              = env_variable('training_samples_file',    '/data/training_samples.json.log')
mqtt_host                               = env_variable('mqtt_host',                'docker.for.mac.localhost')
mqtt_port                               = env_variable('mqtt_port',                '1883',  int)
mqtt_client_id                          = env_variable('mqtt_client_id',           'Main entrance people identifier')
mqtt_topic                              = env_variable('mqtt_topic',               'face_recognition')
mqtt_username                           = env_variable('mqtt_username',            ' ')
mqtt_password                           = env_variable('mqtt_password',            ' ')
source_name                             = env_variable('source_name',              'Main entrance:enter')
MAX_DISTANCE_THRESHOLD                  = env_variable('MAX_DISTANCE_THRESHOLD',   '0.2',   float)
TRACKER_MIN_NUMBER_OF_OCCURENCES        = env_variable('MIN_NUMBER_OF_OCCURENCES', '1',     int)
TRACKER_MAX_NUMBER_OF_FRAMES_TO_PROCESS = env_variable('MAX_NUMBER_OF_FRAMES_TO_PROCESS', '20', int)
TRACKER_MIN_NUMBER_OF_MISSES            = env_variable('MIN_NUMBER_OF_MISSES',     '50',    int)

# [LEARNING]: OpencvVideoSource seems slightly faster
camera = OpencvVideoSource(video_device_id = video_device, use_thread = True, limit_frame_rate = limit_frame_rate, resolution = (640, 480)).start_camera()
# camera = ImutilsVideoSource(video_device_id = -1, use_thread = True).start_camera()

dataset = Dataset(state_file_path)
model = Model(dataset, MAX_DISTANCE_THRESHOLD = MAX_DISTANCE_THRESHOLD, training_samples_file_path = training_samples_file_path)

detector = KnownFaceDetector(model, face_detector_class = DlibFaceDetector)
# detector = KnownFaceDetector(model, face_detector_class = OpencvDnnFaceDetector)

messenger = MqttMessenger(host = mqtt_host, port = mqtt_port, client_id = mqtt_client_id, username = mqtt_username, password = mqtt_password, topic = mqtt_topic, source_name = source_name)
tracker = Tracker(messenger, MIN_NUMBER_OF_OCCURENCES = TRACKER_MIN_NUMBER_OF_OCCURENCES, MAX_NUMBER_OF_FRAMES_TO_PROCESS = TRACKER_MAX_NUMBER_OF_FRAMES_TO_PROCESS, MIN_NUMBER_OF_MISSES = TRACKER_MIN_NUMBER_OF_MISSES, enable_events = enable_events)
updater = DataUpdater(dataset, messenger, lambda : camera.get_rgb_bgr_image()[0])
fps = Fps()
if enable_display:
    display = DisplayWindow()

fps.start()
updater.listen()

not_ready_printed = False
frame_number = 0


while True:
# while fps.elapsed()<15:
    frame_number = frame_number + 1
    (img, bgr_image) = camera.get_rgb_bgr_image()
    if img is None:
        if not not_ready_printed:
            not_ready_printed=True
            print('image not available yet')
        continue

    if not_ready_printed:
        not_ready_printed = False
        print('camera now ready')
    # cv2.imwrite('./%04d.png' % frame_number, img)

    detected_faces = detector.identify_faces(img,100)
    tracker.update(detected_faces)
    if enable_display:
        display.show(bgr_image, detected_faces)
    # print(detected_faces)
    fps.update()
    if frame_number % 10 == 0 and verbose_logging:
        print('program: ' + fps.info())
        print('Camera: ' + camera.fps.info())
    # time.sleep(0.01)
