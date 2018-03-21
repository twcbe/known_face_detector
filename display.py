import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX
font_thickness = 2
font_scale = .75
window_name = "imageView"

class DisplayWindow(object):
    """A class that encapsulates a display that can show face images with some overlayed content"""
    def __init__(self, terminate_on_close = True, fullscreen=True):
        super(DisplayWindow, self).__init__()
        self.terminate_on_close = terminate_on_close
        self.show_window(fullscreen)

    def show_window(self, fullscreen):
        if fullscreen:
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.moveWindow(window_name, 0, 0)
            cv2.resizeWindow(window_name, 1000, 1000)
            # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

    # image parameter must be bgr image
    def show(self, image, detections):
        for detection in detections:
            bb = detection['bb'] # dlib.rectangle
            landmarks = detection['landmarks']
            cv2.rectangle(image,(bb.left(), bb.top()),(bb.right(), bb.bottom()),(128,200,200),1)
            bb_top_left=(bb.left(), bb.top()-2)
            forehead=landmarks[18]
            text_position = bb_top_left
            name = get_name(detection)
            cv2.putText(image,'{}'.format(name), text_position, font, font_scale, (32,128,128), font_thickness+5)
            cv2.putText(image,'{}'.format(name), text_position, font, font_scale, (255,255,255), font_thickness)
            draw_landmarks(image, landmarks)
        self.terminate_if_window_closed()
        cv2.imshow(window_name, image)
        cv2.waitKey(1) # needed to actually show window onscreen. 

    def terminate_if_window_closed(self):
        if cv2.getWindowProperty(window_name, 0) < 0 and self.terminate_on_close:
            #window is not visible
            thread.interrupt_main()

def get_name(detection):
    person = detection['predicted_person']
    if person is not None:
        return person['name']
    closest = detection['closest_matching_person'] 
    if closest is not None:
        return "Unknown (closest:{})".format(closest["name"])
    return "Unknown"

def draw_landmarks(image, landmarks):
    cv2.polylines(image, np.int32([landmarks[0:17]]),  0, (128,128,0),1) #face
    cv2.polylines(image, np.int32([landmarks[17:22]]), 0, (128,128,0),1) #left eyebrow
    cv2.polylines(image, np.int32([landmarks[22:27]]), 0, (128,128,0),1) #right eyebrow
    cv2.polylines(image, np.int32([landmarks[27:31]]), 0, (128,128,0),1) #nose
    cv2.polylines(image, np.int32([landmarks[31:36]]), 0, (128,128,0),1) #nostrils
    cv2.polylines(image, np.int32([landmarks[36:42]]), 1, (128,128,0),1) #left eye
    cv2.polylines(image, np.int32([landmarks[42:48]]), 1, (128,128,0),1) #right eye
    cv2.polylines(image, np.int32([landmarks[48:60]]), 1, (128,128,0),1) #lips outer
    cv2.polylines(image, np.int32([landmarks[60:68]]), 1, (128,128,0),1) #lips outer
    # prev_landmark=landmarks[-1]
    # for landmark in landmarks:
    #     # cv2.circle(image, landmark, 1, (0, 0, 255), -1)
    #     cv2.line(image, prev_landmark, landmark, (0, 0, 255), 1)
    #     prev_landmark = landmark
