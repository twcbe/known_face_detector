from face_detector import DlibFaceDetector
import openface
import dlib
import cv2
import time
from utils import *
import numpy as np
from image_processor import ImageProcessor


dlibFacePredictor = '/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat' # TODO: possible perf improvement reduce landmarks
scale = 2

class KnownFaceDetector():
    def __init__(self, model, trained_classifier_file="tw_coimbatore_faces_classifier", face_detector_class = DlibFaceDetector):
        self.face_detector = face_detector_class()
        self.image_processor = ImageProcessor()
        self.model = model

    def identify_faces(self, image, max_faces=1):
        # returns [{known: false, bb: rect()}, {known: true, bb: rect(), representation: rep}]
        return [self.identify_face(image, bounding_box) for bounding_box in self.face_detector.detect_faces(image, max_faces)]

    def identify_face(self, image, bounding_box):
        (aligned_face, landmarks, rep) = self.image_processor.get_representation(image, bounding_box)
        (predicted_person, closest_matching_person, distance) = self.model.predict(rep)
        result =  {
            'known': predicted_person != None,
            'bb': Rectangle(bounding_box.left(),bounding_box.top(),bounding_box.right(),bounding_box.bottom()),
            'predicted_person': predicted_person and predicted_person.serialize(),
            'closest_matching_person': closest_matching_person and closest_matching_person.serialize(),
            'distance': distance,
            'landmarks': landmarks
        }
        return result
