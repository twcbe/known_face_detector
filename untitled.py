rm -rf /usr/local/lib/python2.7/dist-packages/openface
ln -s /host/repo/openface/openface/ /usr/local/lib/python2.7/dist-packages/openface

import openface
import cv2
import os
import time
import sklearn
import sklearn.cluster
import numpy as np

imgPaths = os.listdir('cbe-aligned-images/all_images')


def getRep(imgPath):
    bgrImg = cv2.imread('cbe-aligned-images/all_images/{}'.format(imgPath));
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    start = time.time()
    rep = net.forward(rgbImg)
    print("net.forward took {} seconds for image: {}".format(time.time() - start, imgPath))
    return rep


net = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')
reps = np.array([getRep(imgPath) for imgPath in imgPaths])

X = reps

start = time.time()
ms = sklearn.cluster.MeanShift(0.44).fit(X)
time.time() - start
clusters = ms.predict(X)

uniqs = np.unique(clusters,return_counts=1)
cluster_leader_board = sorted(zip(uniqs[0],uniqs[1]), key = lambda x: -x[1]) # [(cluster, count)]
print('total clusters : {}'.format(cluster_leader_board[0][1]))
np.array(imgPaths)[clusters==16]
print("open '" + "' '".join(np.array(imgPaths)[clusters==5]) + "'")

for x in xrange(0, cluster_leader_board[0][1]):
    print("open '" + "' '".join(np.array(imgPaths)[clusters==x]) + "'")


align = openface.AlignDlib('dlib-models/shape_predictor_68_face_landmarks.dat')
bb = align.getLargestFaceBoundingBox(rgbImg)
alignedFace = align.align(96, rgbImg, bb, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
rep=net.forward(alignedFace)







def print_cluster_counts(bw):
    clusters = sklearn.cluster.MeanShift(bw).fit(X).predict(X)
    abc=np.unique(clusters,return_counts=1)[1]
    print(len(abc))
    print(sorted(abc,reverse=True))

[print_cluster_counts(bw) for bw in np.arange(0.5,0.3,-0.01)]
# cluster.SpectralClustering(n_clusters=params['n_clusters'], eigen_solver='arpack',
#         affinity="nearest_neighbors")