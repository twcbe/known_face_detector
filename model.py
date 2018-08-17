from sklearn.naive_bayes import GaussianNB
from image_processor import ImageProcessor
from sklearn.naive_bayes import GaussianNB
from datetime import datetime
from utils import *
import numpy as np

MIN_CONFIDENCE_THRESHOLD=0.9

class Model(object):
    def __init__(self, dataset, MAX_DISTANCE_THRESHOLD=0.2, training_samples_file_path = None):
        self.MAX_DISTANCE_THRESHOLD = MAX_DISTANCE_THRESHOLD
        self.dataset = dataset
        self.training_samples_file_path = training_samples_file_path
        self.image_processor = ImageProcessor()
        self.train_classifier()
        self.dataset.on_data_change(self.train_classifier)

    def train_classifier(self):
        print(">>> Re-Training classifier...")
        (X, Y) = self.dataset.get_training_data()
        print(">>> dataset length {}".format(len(X)))
        if len(Y) > 1:
            gnb_classifer = GaussianNB()
            gnb_classifer.fit(X,Y)
            self.classifier = gnb_classifer
        else:
            self.classifier = None

    def predict(self, rep):
        if self.classifier is None:
            print(">>> classifier is None. Not predicting... Please add atleast two different people data")
            return (None, None, None)
        probabilities = self.classifier.predict_proba([rep])[0]
        high_confidence = probabilities > MIN_CONFIDENCE_THRESHOLD
        predicted_cluster = None
        nearest_class = None
        distance = None
        if np.count_nonzero(high_confidence) == 1:
            nearest_class = np.where(high_confidence)[0][0]
            confidence = max(probabilities)
            (all_reps, clusters) = self.dataset.get_training_data()
            if nearest_class in clusters:
                distance = compute_mean_euclidean_distance(np.array(all_reps), np.array(clusters), rep, nearest_class)
                if distance < self.MAX_DISTANCE_THRESHOLD:
                    predicted_cluster = nearest_class
        predicted_person = self.dataset.get_person_with_cluster_id(predicted_cluster)
        closest_match = self.dataset.get_person_with_cluster_id(nearest_class)
        if distance is not None:
            self.log_training_samples(rep, distance, closest_match)
        return (predicted_person, closest_match, distance)

    def log_training_samples(self, rep, distance, closest_person):
        if self.training_samples_file_path:
            append_to_file(self.training_samples_file_path, {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:23],'rep': rep.tolist(), 'distance': distance, 'closest_person': closest_person.serialize()})

def compute_mean_euclidean_distance(all_reps, clusters, face_rep, predicted_cluster):
    predicted_cluster_reps = all_reps[clusters==predicted_cluster]
    distances = np.array([distance_between(rep, face_rep) for rep in predicted_cluster_reps])
    min_distance = np.min(distances) # we are only taking minimum most distance. Can we say if there are multiple closer representations, it is a better match?
    return min_distance

def distance_between(a,b):
    d = a.ravel() - b.ravel()
    return np.dot(d,d)
