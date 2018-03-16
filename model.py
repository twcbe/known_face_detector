from sklearn.naive_bayes import GaussianNB
from image_processor import ImageProcessor
from sklearn.naive_bayes import GaussianNB

class Model(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.image_processor = ImageProcessor()
        self.train_classifier()
        self.dataset.on_data_change(self.train_classifier)

    def train_classifier(self):
        (X, Y) = self.dataset.get_training_data()
        gnb_classifer = GaussianNB()
        gnb_classifer.fit(X,Y)
        self.classifier = gnb_classifer

    def predict(self, rep):
        probabilities = self.classifier.predict_proba([rep])[0]
        high_confidence = probabilities > MIN_CONFIDENCE_THRESHOLD
        if np.count_nonzero(high_confidence) == 1:
            nearest_class = np.where(high_confidence)[0][0]
            confidence = max(probabilities)
            distance = compute_mean_euclidean_distance(self.reps, self.clusters, rep, nearest_class)
            if distance < MAX_DISTANCE_THRESHOLD:
                predicted_cluster = nearest_class
        predicted_person = self.dataset.get_person_with_cluster_id(predicted_cluster)
        closest_match = self.dataset.get_person_with_cluster_id(nearest_class)
        return (predicted_person, closest_match, distance)

def compute_mean_euclidean_distance(all_reps, clusters, face_rep, predicted_cluster):
    predicted_cluster_reps = all_reps[clusters==predicted_cluster]

    distances = np.array([distance_between(rep, face_rep) for rep in predicted_cluster_reps])
    average_distance = np.average(distances)
    return average_distance

def distance_between(a,b):
    d = a.ravel() - b.ravel()
    return np.dot(d,d)