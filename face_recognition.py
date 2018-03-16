
import openface
import cv2
import os
import time
import sklearn
import sklearn.cluster
import numpy as np

class face_recognisor():


    
    
    def __init__(self):
        print("Initialised the face recognisor")


    def getRepresentation(self, aligned_face):
        # net = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')
        print("This will return the representation of the face")
        # start = time.time()
        # rep = net.forward(face)
        # print("net.forward took {} seconds for image: {}".format(time.time() - start, imgPath))
        # return rep