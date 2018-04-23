from sklearn.naive_bayes import GaussianNB
from image_processor import ImageProcessor
from sklearn.naive_bayes import GaussianNB
import numpy as np

MIN_CONFIDENCE_THRESHOLD=0.9
MAX_DISTANCE_THRESHOLD=0.25

class Model(object):
    def __init__(self, dataset):
        self.dataset = dataset
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
        closest_match = None
        nearest_class = None
        if np.count_nonzero(high_confidence) == 1:
            nearest_class = np.where(high_confidence)[0][0]
            confidence = max(probabilities)
            (all_reps, clusters) = self.dataset.get_training_data()
            distance = compute_mean_euclidean_distance(np.array(all_reps), np.array(clusters), rep, nearest_class)
            if distance < MAX_DISTANCE_THRESHOLD:
                predicted_cluster = nearest_class
        predicted_person = self.dataset.get_person_with_cluster_id(predicted_cluster)
        closest_match = self.dataset.get_person_with_cluster_id(nearest_class)
        return (predicted_person, closest_match, distance)

def compute_mean_euclidean_distance(all_reps, clusters, face_rep, predicted_cluster):
    predicted_cluster_reps = all_reps[clusters==predicted_cluster]

    distances = np.array([distance_between(rep, face_rep) for rep in predicted_cluster_reps])
    average_distance = np.min(distances)
    return average_distance

def distance_between(a,b):
    d = a.ravel() - b.ravel()
    return np.dot(d,d)
