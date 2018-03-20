import openface
import time
from known_face_detector import DlibFaceDetector

class ImageProcessor:
    def __init__(self, face_detector_class = DlibFaceDetector, image_dimension=96, openface_model_path = '/root/openface/models/openface/nn4.small2.v1.t7', dlib_face_landmarks_model = '/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat'):
        self.net = openface.TorchNeuralNet(openface_model_path)
        self.face_detector = face_detector_class()
        self.face_aligner = openface.AlignDlib(dlib_face_landmarks_model)
        self.image_dimension = image_dimension

    def get_representation(self, image):
        bounding_box = self.face_detector.detect_faces(image, max_faces=1)[0]
        (aligned_face, landmarks, rep) = get_representation(image, bounding_box)
        return rep

    def get_representation(self, image, bounding_box):
        (aligned_face, landmarks) = self.align_face(image, bounding_box)
        if aligned_face is None:
            return (None, None, None)
        rep = self.net.forward(aligned_face)
        return (aligned_face, landmarks, rep)

    def align_face(self, image, bounding_box):
        start=time.time()
        landmarks=self.face_aligner.findLandmarks(image, bounding_box)
        # print('>>> findLandmarks took %.3f seconds' % (time.time() - start))
        start=time.time()
        aligned_face = self.face_aligner.align(
            self.image_dimension,
            image,
            bounding_box,
            landmarks,
            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        # print('>>> align_face took %.3f seconds' % (time.time() - start))
        # if aligned_face is None:
            # print("Unable to align image.")
        return (aligned_face, landmarks)
