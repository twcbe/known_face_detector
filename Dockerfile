FROM bamos/openface

RUN apt-get update && apt-get install -y v4l-utils && pip install imutils && pip install paho-mqtt

WORKDIR /known_face_detector

COPY . .

ENV ENV production

CMD ["python", "main.py"]
