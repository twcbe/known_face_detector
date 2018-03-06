import openface
import dlib
import cv2
import time
import pickle
from sklearn.naive_bayes import GaussianNB
from utils import *

dlibFacePredictor = '/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat' # TODO: possible perf improvement reduce landmarks
scale = 1
MIN_CONFIDENCE_THRESHOLD=0.9
MAX_DISTANCE_THRESHOLD=0.5

class KnownFaceDetector():
    def __init__(self, trained_classifier_file="tw_coimbatore_faces_classifier"):
        start=time.time()
        self.net = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')
        print('>>> initialised torch network in %.3f seconds' % (time.time() - start))
        start=time.time()
        self.face_detector = dlib.get_frontal_face_detector()
        print('>>> get_frontal_face_detector took %.3f seconds' % (time.time() - start))
        self.image_dimension = 96
        start=time.time()
        self.align = openface.AlignDlib(dlibFacePredictor)
        print('>>> AlignDlib took %.3f seconds' % (time.time() - start))
        self.classifier = load_file(trained_classifier_file)

    def detect_faces(self, image, max_faces=1):
        bounding_boxes = self.get_all_bounding_boxes(image)
        # returns [{known: false, bb: rect()}, {known: true, bb: rect(), representation: rep}]
        return [self.detect_face(image, bounding_box) for bounding_box in bounding_boxes[0:max_faces]]

    def get_all_bounding_boxes(self, image):
        start=time.time()
        image = cv2.resize(image, (0,0), fx=1.0/scale, fy=1.0/scale)
        bounding_boxes = self.face_detector(image, 1);
        print('>>> face_detector took %.3f seconds' % (time.time() - start))
        start=time.time()
        bounding_boxes = sorted(bounding_boxes, key=lambda rect: rect.width() * rect.height())
        print('>>> sorting bounding_boxes took %.3f seconds' % (time.time() - start))
        return [dlib.rectangle(bb.left()*scale,bb.top()*scale,bb.right()*scale,bb.bottom()*scale) for bb in bounding_boxes]

    def detect_face(self, image, bounding_box):
        aligned_face = self.align_face(image, bounding_box)
        rep = self.get_representation(aligned_face)
        # classifier goes in here
        # TODO: NEXT
        (predicted_class, nearest_class, distance, classifier_confidence) = predict_cluster(rep)
        # predicted_class = self.classifier.predict_proba([rep])[0]
        return {
            'known': predicted_class != None,
            'bb': bounding_box,
            'class': predicted_class,
            'predicted_class': predicted_class,
            'nearest_class': nearest_class,
            'distance': distance,
            'classifier_confidence': classifier_confidence
        }

    def predict_cluster(self, rep):
        probabilities = self.gnb.predict_proba([rep])[0]

        high_confidence = probabilities > MIN_CONFIDENCE_THRESHOLD
        # print(high_confidence)
        if np.count_nonzero(high_confidence) == 1:
            predicted_cluster = np.where(high_confidence)[0][0]
            confidence = max(probabilities)
            # print("predicted_cluster")
            # print(predicted_cluster)
            distance = compute_mean_euclidean_distance(self.reps, self.clusters, rep, predicted_cluster)
            if distance < MAX_DISTANCE_THRESHOLD:
                return (predicted_cluster, predicted_cluster, distance, confidence)
            return (None, predicted_cluster, distance, confidence)
        return (None, None, None, np.count_nonzero(high_confidence))

    def align_face(self, image, bounding_box):
        start=time.time()
        landmarks=self.align.findLandmarks(image, bounding_box)
        print('>>> findLandmarks took %.3f seconds' % (time.time() - start))
        start=time.time()
        aligned_face = self.align.align(
            self.image_dimension,
            image,
            bounding_box,
            landmarks,
            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        print('>>> align_face took %.3f seconds' % (time.time() - start))
        if aligned_face is None:
            print("Unable to align image.")
        return aligned_face

    def get_representation(self, aligned_face_image):
        start=time.time()
        rep = self.net.forward(aligned_face_image)
        print('>>> net.forward pass took %.3f seconds' % (time.time() - start))
        return rep
