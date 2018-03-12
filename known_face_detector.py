from face_detector import DlibFaceDetector
import openface
import dlib
import cv2
import time
import pickle
from sklearn.naive_bayes import GaussianNB
from utils import *
import numpy as np
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt


dlibFacePredictor = '/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat' # TODO: possible perf improvement reduce landmarks
scale = 2
MIN_CONFIDENCE_THRESHOLD=0.9
MAX_DISTANCE_THRESHOLD=0.5
auth = {
        'username':"socnhliq",
        'password':"7wrIE_dxtWE6"
    }
class KnownFaceDetector():
    def __init__(self, trained_classifier_file="tw_coimbatore_faces_classifier", face_detector_class = DlibFaceDetector):
        start=time.time()
        self.net = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')
        # print('>>> initialised torch network in %.3f seconds' % (time.time() - start))
        self.face_detector = face_detector_class()
        self.image_dimension = 96
        start=time.time()
        self.align = openface.AlignDlib(dlibFacePredictor)
        # print('>>> AlignDlib took %.3f seconds' % (time.time() - start))
        self.classifier = load_file(trained_classifier_file)
        self.reps = load_file("reps")
        self.clusters = load_file("clusters")
        print("Publishing event to subscriber")
        auth = {
            'username':"socnhliq",
            'password':"7wrIE_dxtWE6"
        }

        publish.single("face/known",
            payload = "Initialised",
            hostname = "m11.cloudmqtt.com",
            client_id = "publisher",
            auth = auth,
            port = 10833,
            protocol = mqtt.MQTTv311)

    def identify_faces(self, image, max_faces=1):
        # returns [{known: false, bb: rect()}, {known: true, bb: rect(), representation: rep}]
        return [self.identify_face(image, bounding_box) for bounding_box in self.face_detector.detect_faces(image, max_faces)]

    def identify_face(self, image, bounding_box):
        (aligned_face, landmarks) = self.align_face(image, bounding_box)
        rep = self.get_representation(aligned_face)
        # classifier goes in here
        # TODO: NEXT
        (predicted_class, nearest_class, distance, classifier_confidence) = self.predict_cluster(rep)
        # predicted_class = self.classifier.predict_proba([rep])[0]
        result =  {
            'known': predicted_class != None,
            'bb': bounding_box,
            'class': predicted_class,
            'predicted_class': predicted_class,
            'nearest_class': nearest_class,
            'distance': distance,
            'landmarks': landmarks,
            'classifier_confidence': classifier_confidence
        }
        publish_event("Face detected: Class - {}".format(predicted_class))
        return result

    def predict_cluster(self, rep):
        probabilities = self.classifier.predict_proba([rep])[0]

        high_confidence = probabilities > MIN_CONFIDENCE_THRESHOLD
        if np.count_nonzero(high_confidence) == 1:
            predicted_cluster = np.where(high_confidence)[0][0]
            confidence = max(probabilities)
            distance = compute_mean_euclidean_distance(self.reps, self.clusters, rep, predicted_cluster)
            if distance < MAX_DISTANCE_THRESHOLD:
                return (predicted_cluster, predicted_cluster, distance, confidence)
            return (None, predicted_cluster, distance, confidence)
        return (None, None, None, np.count_nonzero(high_confidence))
        

    def align_face(self, image, bounding_box):
        start=time.time()
        landmarks=self.align.findLandmarks(image, bounding_box)
        # print('>>> findLandmarks took %.3f seconds' % (time.time() - start))
        start=time.time()
        aligned_face = self.align.align(
            self.image_dimension,
            image,
            bounding_box,
            landmarks,
            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        # print('>>> align_face took %.3f seconds' % (time.time() - start))
        if aligned_face is None:
            # print("Unable to align image.")
            pass
        return (aligned_face, landmarks)

    def get_representation(self, aligned_face_image):
        start=time.time()
        rep = self.net.forward(aligned_face_image)
        # print('>>> net.forward pass took %.3f seconds' % (time.time() - start))
        return rep

def compute_mean_euclidean_distance(all_reps, clusters, face_rep, predicted_cluster):
    predicted_cluster_reps = all_reps[clusters==predicted_cluster]

    distances = np.array([distance_between(rep, face_rep) for rep in predicted_cluster_reps])
    average_distance = np.average(distances)

    # # print("Mean Euclidean distance:")
    # # print(average_distance)
    return average_distance

def distance_between(a,b):
    d = a.ravel() - b.ravel()
    return np.dot(d,d)

def publish_event(result):
    publish.single("face/known",
        payload = result,
        hostname = "m11.cloudmqtt.com",
        client_id = "publisher",
        auth = auth,
        port = 10833,
        protocol = mqtt.MQTTv311)
