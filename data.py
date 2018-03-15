import utils
import openface
import cv2

class Dataset:
	data = []

	def __init__(self):
		if(utils.exists("dataset")):
			self.data = utils.load_file("dataset")

	def add_entry(self, rep, cluster_id):
		self.data.append((rep, cluster_id))
		print(self.data)
		utils.save_file(self.data, "dataset")

	def add_entry_given_image_path(self, image_path, cluster_id):
		# ip = ImageProcessor(image_path)
		# rep = ip.get_representation(image)

		rep = ImageProcessor(image_path).get_representation()
		print("Rep returned")
		print(rep)
		self.add_entry(rep, cluster_id)

class ImageProcessor:
	def __init__(self, image_path):
		self.net = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')
		print("---------------------------")
		print("Initialised image processor")
		self.image = cv2.imread(image_path)
		if self.image is not None:
			print("Image found")
		else:
			print("Unable to find image")

	def get_representation(self):
		print("Generating rep")
		rep = self.net.forward(self.image)
		return rep
def main():
	image_path = "cbe-aligned-images/cluster-0/Copy of IMG_2020_2.png"
	ds = Dataset()
	print(ds.data)
	ds.add_entry_given_image_path(image_path, 0)

if __name__ == "__main__":
	main()

