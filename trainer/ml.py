from os import path, mkdir
import time
import sklearn.cluster
import numpy as np
from nn import NeuralNetwork as nn
import shutil 
np.set_printoptions(threshold = np.nan)
from sklearn.naive_bayes import GaussianNB
import pickle

MIN_CONFIDENCE_THRESHOLD=0.9
MAX_DISTANCE_THRESHOLD=0.5
NUMBER_OF_CLUSTERS_FOR_TRAINING=20
NUMBER_OF_ENTRIES_IN_EACH_CLUSTER_FOR_TRAINING=10

class MeanShiftClassifier:

	reps = []
	paths = []
	clusters = []

	def __init__(self, reps, paths):
		self.reps = np.array(reps)
		self.paths = paths
		print("Mean Shift Classifier initialised")

	def train(self, data):
		X = data[0]
		Y = data[1]
		Z = data[2]

		self.gnb = GaussianNB()
		self.gnb.fit(X,Y)
		save(self.gnb, "tw_coimbatore_faces_classifier")

		predicted_clusters=self.gnb.predict(X)
		probabilities = self.gnb.predict_proba(X)

	def getRepIndex(self, rep):
		return np.where(self.reps==rep)[0][0]


	def test(self, known_test_data, unknown_test_data):
		test_data = zip(known_test_data[0], # reps
			known_test_data[1], # clusters
			known_test_data[2], # path
			np.ones(len(known_test_data[0]),dtype=bool) # known?
		) # + zip(unknown_test_data[0],unknown_test_data[1],np.zeros(len(known_test_data[0]),dtype=bool))

		results=[]
		for (rep, cluster, path, is_known) in test_data:
			(predicted_cluster, classifier_prediction, distance, confidence) = self.predict_cluster(rep)
			result = verify(predicted_cluster, cluster, is_known)
			if not result:
				print(">> rep[%4d] cluster=%2d final_prediction=%4s predicted_cluster=%4s distance=%f confidence=%f path=%s" % (self.getRepIndex(rep), cluster, predicted_cluster, classifier_prediction, distance, confidence, path))
			results.append(result)



		print("====================================")
		print("results:")
		print(results)
		print("correct predictions:")
		print(np.count_nonzero(results))
		print("total test entries:")
		print(len(results))
		print("percentage accuracy:")
		print(100.0 * np.count_nonzero(results) / len(results))
		print("====================================")


	def classify(self, data):
		X = data[0]
		Y = data[1]
		Z = data[2]

		gnb = GaussianNB()
		gnb.fit(X,Y)
		gnb_pickle_filehandle = open("gnb_classifier", "wb")
		pickle.dump(gnb, gnb_pickle_filehandle)
		gnb_pickle_filehandle.close()

		predicted_clusters=gnb.predict(X)
		probabilities = gnb.predict_proba(X)

		print("Probabilities")
		print(len(probabilities))
		print(type(probabilities))
		print(probabilities.shape)
		#print(probabilities[0:10], Y[0:10])

		print("Scores")
		scores = gnb.score(X, Y)
		print(scores)
		print("Class prior: {}".format(gnb.class_prior_))
		print("Class count: {}".format(gnb.class_count_))

		print("Representations")
		print(len(X))
		print(type(X))
		print(X.shape)

		print("\n\n\nKnown")
		test_known_rep = self.reps[np.where(self.paths=="IMG_20170912_145024_4.png")]
		test_known_prediction = gnb.predict(test_known_rep)
		test_known_prob = gnb.predict_proba(test_known_rep)

		print(test_known_prediction)
		print(test_known_prob)
		print("Max confidences: {}".format(test_known_prob[0][np.argmax(test_known_prob)]))

		mean_distance = compute_mean_euclidean_distance(self.reps, self.clusters, test_known_rep, test_known_prediction)

		print("\n\n\nUnknown")
		test_unknown_rep = self.reps[np.where(self.paths=="DSC_5213_10.png")]
		test_unknown_prediction = gnb.predict(test_unknown_rep)
		test_unknown_prob = gnb.predict_proba(test_unknown_rep)
		print("Max confidence: {}".format(test_unknown_prob[0][np.argmax(test_unknown_prob)]))

		print(test_unknown_prediction)
		print(test_unknown_prob)

		mean_distance = compute_mean_euclidean_distance(self.reps, self.clusters, test_unknown_prediction, test_unknown_rep)

	def cluster_reps(self):
		ms = sklearn.cluster.MeanShift(0.44).fit(self.reps)
		save(ms, "ms_clusterer")

		self.clusters=np.array(ms.predict(self.reps))
		save(self.reps, "reps")
		save(self.clusters, "clusters")
		known_data_mask = self.clusters<NUMBER_OF_CLUSTERS_FOR_TRAINING


		

		first_n_mask = np.logical_and(known_data_mask, get_first_n_mask(self.clusters, n=NUMBER_OF_ENTRIES_IN_EACH_CLUSTER_FOR_TRAINING))
		print("First n mask: {}".format(first_n_mask))
		print("Length: {}".format(len(first_n_mask)))
		# first_n_mask = np.pad(first_n_mask, (0, (1015 - len(first_n_mask))), 'constant', constant_values = False)
		print("First n mask: {}".format(first_n_mask))
		print("Length: {}".format(len(first_n_mask)))


		known_train_data_mask =  first_n_mask
		known_test_data_mask  =  np.logical_and(known_data_mask, ~first_n_mask)
		unknown_data_mask     = ~known_data_mask

		print("=====================")
		print("Count of entries:")
		print("first_n_mask")
		print(np.count_nonzero(first_n_mask))
		print("known_data_mask")
		print(np.count_nonzero(known_data_mask))
		print("known_train_data_mask")
		print(np.count_nonzero(known_train_data_mask))
		print("known_test_data_mask")
		print(np.count_nonzero(known_test_data_mask))
		print("unknown_data_mask")
		print(np.count_nonzero(unknown_data_mask))
		print("=====================")
		# print("Known train data mask: {}".format(known_train_data_mask))
		# print("Mask shape: {}".format(known_train_data_mask.shape))
		# print("Reps shape: {}".format(self.reps.shape))
		# print(self.reps[known_train_data_mask])

		train_data=(
			self.reps[known_train_data_mask],
			self.clusters[known_train_data_mask],
			self.paths[known_train_data_mask])

		known_test_data=(
			self.reps[known_test_data_mask],
			self.clusters[known_test_data_mask],
			self.paths[known_test_data_mask])

		unknown_test_data=(
			self.reps[unknown_data_mask],
			self.clusters[unknown_data_mask],
			self.paths[unknown_data_mask])

		save(train_data, "train_data")
		save(known_test_data, "known_test_data")
		save(unknown_test_data, "unknown_test_data")

		self.train(train_data)
		self.test(known_test_data, unknown_test_data)
		# self.classify(train_data)

		# for (p, cluster) in zip(self.paths, self.clusters):
		# 	print("Sorting {} into {}".format(p, cluster))
		# 	self.sortImages(p, cluster)

	def sortImages(self, p, cluster):	
		dir = "./../cbe-aligned-images/cluster-{}".format(cluster)
		destination = path.join(dir, p)
		p = path.join("./../Archive/cbe-aligned-images/all_images", p)
		if path.exists(dir):
			# print("Path exists")
			shutil.copy(p, dir)
			# print("File copied")
		else:
			# print("Path does not exist")
			mkdir(dir)
			# print("Directory created")
			shutil.copy(p, dir)
			# print("File copied")

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

def compute_mean_euclidean_distance(all_reps, clusters, face_rep, predicted_cluster):
	predicted_cluster_reps = all_reps[clusters==predicted_cluster]

	distances = np.array([distance_between(rep, face_rep) for rep in predicted_cluster_reps])
	average_distance = np.average(distances)

	# print("Mean Euclidean distance:")
	# print(average_distance)
	return average_distance

def distance_between(a,b):
	d = a.ravel() - b.ravel()
	return np.dot(d,d)


def verify(a,b,isNotNone):
	if isNotNone:
		# a should not be None
		return a == b
	#a should be None
	return a is None

def save(data, name):
	file_handle = open(name+".pkl","wb")
	pickle.dump(data, file_handle)
	file_handle.close()

def load(name):
	file_handle = open(name+".pkl","rb")
	data = pickle.load(file_handle)
	file_handle.close()
	return data

def get_first_n(arr, clusters,n):
	cluster_ids = sorted(set(clusters))
	return flatten([arr[clusters==cluster_id][0:n] for cluster_id in cluster_ids])

def flatten(l):
	return [item for sublist in l for item in sublist]


def get_first_n_mask(clusters,n):
	cluster_counts = {cluster:n for cluster in sorted(set(clusters))}
	print(cluster_counts)
	mask=np.zeros((len(clusters)),dtype=bool)
	for i in range(0,len(clusters)):
		if cluster_counts[clusters[i]]>0:
			mask[i]=True
			cluster_counts[clusters[i]]=cluster_counts[clusters[i]]-1
	return mask
 
