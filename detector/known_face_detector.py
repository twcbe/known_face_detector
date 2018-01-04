import openface
import dlib
import cv2
import time

dlibFacePredictor = '/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat' # TODO: possible perf improvement reduce landmarks
scale = 2

class KnownFaceDetector():
    def __init__(self):
        start=time.time()
        self.net = openface.TorchNeuralNet('/root/openface/models/openface/nn4.small2.v1.t7')
        print('>>> initialised torch network in %.3f seconds' % (time.time() - start))
        start=time.time()
        self.face_detector = dlib.get_frontal_face_detector()
        print('>>> get_frontal_face_detector took %.3f seconds' % (time.time() - start))
        self.image_dimension = 96
        start=time.time()
        self.align = openface.AlignDlib(dlibFacePredictor)
        print('>>> AlignDlib took %.3f seconds' % (time.time() - start))

    def detect_faces(self, image, max_faces=1):
        bounding_boxes = self.get_all_bounding_boxes(image)
        # returns [{known: false, bb: rect()}, {known: true, bb: rect(), representation: rep}]
        return [self.detect_face(image, bounding_box) for bounding_box in bounding_boxes[0:max_faces]]

    def get_all_bounding_boxes(self, image):
        start=time.time()
        image = cv2.resize(image, (0,0), fx=1.0/scale, fy=1.0/scale)
        bounding_boxes = self.face_detector(image, 0);
        print('>>> face_detector took %.3f seconds' % (time.time() - start))
        start=time.time()
        bounding_boxes = sorted(bounding_boxes, key=lambda rect: rect.width() * rect.height())
        print('>>> sorting bounding_boxes took %.3f seconds' % (time.time() - start))
        return [dlib.rectangle(bb.left()*scale,bb.top()*scale,bb.right()*scale,bb.bottom()*scale) for bb in bounding_boxes]

    def detect_face(self, image, bounding_box):
        aligned_face = self.align_face(image, bounding_box)
        rep = self.get_representation(aligned_face)
        return {
            'known': False, 'bb': bounding_box
        }

    def align_face(self, image, bounding_box):
        start=time.time()
        landmarks=self.align.findLandmarks(image, bounding_box)
        print('>>> findLandmarks took %.3f seconds' % (time.time() - start))
        start=time.time()
        aligned_face = self.align.align(
            self.image_dimension,
            image,
            bounding_box,
            landmarks,
            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        print('>>> align_face took %.3f seconds' % (time.time() - start))
        if aligned_face is None:
            print("Unable to align image.")
        return aligned_face

    def get_representation(self, aligned_face_image):
        start=time.time()
        rep = self.net.forward(aligned_face_image)
        print('>>> net.forward pass took %.3f seconds' % (time.time() - start))
        return rep
