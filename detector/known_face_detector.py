# import openface

dlibFacePredictor = '../dlib-models/shape_predictor_68_face_landmarks.dat'

class KnownFaceDetector():
    def detectFaces(image, max_faces=1):
        # returns [{known: false, bb: rect()}, {known: true, bb: rect(), representation: rep}]
        pass