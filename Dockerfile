FROM bamos/openface

RUN apt-get update && apt-get install -y v4l-utils && pip install imutils && pip install paho-mqtt
