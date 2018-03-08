import dlib
import cv2
import time
import numpy as np
from utils import Rectangle

class DlibFaceDetector():
    def __init__(self, scale_input_image = 2):
        start=time.time()
        self.scale_input_image = scale_input_image
        self.dlib_frontal_face_detector = dlib.get_frontal_face_detector()
        # print('>>> get_frontal_face_detector took %.3f seconds' % (time.time() - start))

    """ Returns bounding boxes. Can detect multiple faces/limited fnumber of faces. Sorts faces based on area in descending order by default. """
    def detect_faces(self, image, max_faces=1):
        bounding_boxes = self.get_all_bounding_boxes(image)
        return bounding_boxes[0:max_faces]

    def get_all_bounding_boxes(self, image):
        start=time.time()
        scale = self.scale_input_image
        image = cv2.resize(image, (0,0), fx=1.0/scale, fy=1.0/scale)
        bounding_boxes = self.dlib_frontal_face_detector(image, 1);
        # print('>>> face_detector took %.3f seconds' % (time.time() - start))
        start=time.time()
        bounding_boxes = sorted(bounding_boxes, key=lambda rect: rect.width() * rect.height())
        # print('>>> sorting bounding_boxes took %.3f seconds' % (time.time() - start))
        return [dlib.rectangle(bb.left()*scale,bb.top()*scale,bb.right()*scale,bb.bottom()*scale) for bb in bounding_boxes]


class OpencvDnnFaceDetector():
    def __init__(self, caffe_model_file_path = "res10_300x300_ssd_iter_140000.caffemodel", prototxt_file_path = "deploy.prototxt.txt", confidence_threshold=0.5):
        start=time.time()
        self.net = cv2.dnn.readNetFromCaffe(prototxt_file_path, caffe_model_file_path)
        self.confidence_threshold = confidence_threshold
        print('>>> loading caffe model took %.3f seconds' % (time.time() - start))

    """ Returns bounding boxes. Can detect multiple faces/limited fnumber of faces. Sorts faces based on area in descending order by default. """
    def detect_faces(self, image, max_faces=1):
        bounding_boxes = self.get_all_bounding_boxes(image)
        return bounding_boxes[0:max_faces]

    def get_all_bounding_boxes(self, image):
        # grab the frame dimensions and convert it to a blob
        (h, w) = image.shape[:2]

        start=time.time()
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
            (300, 300), (104.0, 177.0, 123.0))
        print('>>> cv2.dnn.blobFromImage took %.3f seconds' % (time.time() - start))

        # pass the blob through the network and obtain the detections and predictions
        start=time.time()
        self.net.setInput(blob)
        print('>>> net.setInput(blob) took %.3f seconds' % (time.time() - start))
        start=time.time()
        detections = self.net.forward()
        print('>>> dnn face_detector net.forward took %.3f seconds' % (time.time() - start))

        start=time.time()
        bounding_boxes=[]
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is greater than the minimum confidence
            if confidence < self.confidence_threshold:
                continue

            # compute the (x, y)-coordinates of the bounding box for the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            bounding_boxes.append(Rectangle(x1*scale, y1*scale, x2*scale, y2*scale))

        bounding_boxes = sorted(bounding_boxes, key=lambda rect: rect.area())
        print('>>> creating bounding_boxes from dnn face_detector\'s output took %.3f seconds' % (time.time() - start))
        return bounding_boxes
