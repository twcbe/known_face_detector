import openface
import time



class NeuralNetwork:

	net = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')

	def __init__(self):
		print("Neural Network has been initialised.")

	def get_representation(self, aligned_face_image):
		start = time.time()
		rep = self.net.forward(aligned_face_image)
		print("Rep shape: {}".format(rep.shape))
		print(">>> net.forward pass took %.3f seconds" %(time.time() - start))
		return rep
