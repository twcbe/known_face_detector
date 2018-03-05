from os import listdir, path
import cv2 as cv
from ml import MeanShiftClassifier as msc
from nn import NeuralNetwork as nn
import numpy as np
from os import path

np.set_printoptions(threshold = np.nan)
mapper = nn()

reps_file = "./reps.npy"
paths_file = "./paths.npy"

if path.exists(reps_file) and path.exists(paths_file):
	reps = np.load(reps_file)
	aligned_paths = np.load(paths_file)
	learner = msc(reps, aligned_paths)

else:
	reps = []
	aligned_paths = [x for x in listdir("./../Archive/cbe-aligned-images/all_images") if x.endswith('png')]
	for image_path in aligned_paths:
		image_path = path.join("./../Archive/cbe-aligned-images/all_images", image_path)
		bgrImage = cv.imread(image_path)
		if bgrImage is not None:
			rgbImage = cv.cvtColor(bgrImage, cv.COLOR_BGR2RGB)
			reps.append(mapper.get_representation(rgbImage))
		else:
			print("Unable to read image ", image_path)
	np.save(paths_file, aligned_paths)
	np.save(reps_file, reps)
	learner = msc(reps, aligned_paths)


learner.cluster_reps()






