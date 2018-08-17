FROM bamos/openface

RUN apt-get update && apt-get install -y v4l-utils && pip install imutils && pip install paho-mqtt

RUN sudo echo "Asia/Kolkata" > /etc/timezone

WORKDIR /known_face_detector

ENV ENV production

COPY . .

CMD ["python", "main.py"]
