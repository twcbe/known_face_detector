from detector.known_face_detector import KnownFaceDetector

print(type(KnownFaceDetector))
detector = KnownFaceDetector()
print(detector)


import cv2
cap = cv2.VideoCapture(0)

while True:
    ret, bgrImg = cap.read()
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    faces = detector.detectFaces()
    if len(faces) > 0:
        # raise event saying some face detected and if it is known face or not
        pass

