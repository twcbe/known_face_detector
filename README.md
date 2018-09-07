# Known Face Detector

[![CircleCI](https://circleci.com/gh/twlabs/face-recognition-workspace.svg?style=svg&circle-token=a7216b8a8bcb8065391871ca619301bcbefcda75)](https://circleci.com/gh/twlabs/face-recognition-workspace)

Detect and Identify people, and emit events. Uses a modular design, can be connected to other apps using MQTT events.

This program is easier to setup on a linux machine using docker and a camera attached to the system. There are several customizable options detailed below. To quickly get started jump to the [getting started](#getting-started) section below.

In OS X, only network cameras are supported.

The program can be run in headless mode or with display attached. The display shows the recognized person visually. In case the system doesn't recognize a person correctly it will show the next closest matching person in paranthesis. This is not a match, just shown for debugging.

* Enable or disable display: 
  * `-e enable_display=True` (default False, ie. headless)

* The following flags specify to store the state file containing people identities in `./data/people_identifier.json file`.
  * `-v ./data:/data -e state_file=/data/people_identifier.json`

The source of the video feed can be anything that [OpenCV](https://opencv.org/) supports as video source! It could be a camera attached to the computer, a network camera reachable using an rtsp URI, a pre-recorded video file at a given path.

* To specify the source:
  * `-e video_device=-1 --device /dev/video0` choose the first camera attached to the machine.
  * `-e video_device=-1 --device /dev/video1` choose the second camera attached to the machine.
  * `-e video_device="rtsp://<username>:<password>@<ip>/<channel_number>"` choose a network camera reachable using the given URI. Make sure to enter the username, password, ip and channel_number.
  * `-e video_device="/data/video_filename.mp4"` make sure to put the video file in the `./data` folder.

* Specify the mqtt credentials:
  * `Host : -e mqtt_host=<hostname>` (default docker.for.mac.localhost)
  * `Port : -e mqtt_port=<port>` (default 1883)
  * `Topic : -e mqtt_topic=<topic>` (default face_recognition)
  * `Username : -e mqtt_username=<username` (optional)
  * `Password : -e mqtt_password=<password>` (optional)

## Linux:
### Prerequisites:
* docker
* mosquitto server running in local

### Getting Started:
Run the detector in headless mode with camera attached: (no need to clone this repo)
```bash
mkdir data
docker run -it --rm --name="known_face_detector" -v ./data:/data --device /dev/video0 -e video_device=-1 -e state_file=/data/people_identifier.json twcbe/known_face_detector:master
```
(this will start running the recognizer, the logs will be printed on screen)

Run the detector with display and camera attached: (no need to clone this repo)
```bash
mkdir data
DISPLAY=:0 xhost + 127.0.0.1  # enable remote connections to XServer
docker run -it --rm --name="known_face_detector" -v ./data:/data --device /dev/video0 -e enable_display=true --net=host --ipc=host -v /tmp/X11-unix:/tmp/X11-unix -e DISPLAY=:0 -e video_device=-1 -e state_file=/data/people_identifier.json twcbe/known_face_detector:master
```

## OSX:
### Prerequisites:
* [docker](https://www.docker.com/)
* [xquartz](https://www.xquartz.org/) - for displaying video on screen, not necessary for headless mode.
* xquartz -> preferences -> security -> enable `allow connections from network clients` and restart xquartz.
* network camera - required, since OSX does not provide a raw video device, it cannot be forwarded inside the container. One can run the program like a demo using a pre-captured video file too, in which case the network camera is not necessary.
* mosquitto server running in local

### Getting Started:
Run the detector in headless mode with network camera: (no need to clone this repo)
```bash
mkdir data
docker run -it --rm --name="known_face_detector" -v $(pwd)/data:/data -e state_file=/data/people_identifier.json -e video_device="rtsp://<username>:<password>@<ip.ip.ip.ip>/<channel_number>" twcbe/known_face_detector:master
```
Run the detector in headless mode with network camera: (no need to clone this repo)
```bash
mkdir data
DISPLAY=:0 xhost + 127.0.0.1 # enable remote connections to XServer; required once after every restart of XQuartz
docker run -it --rm --name="known_face_detector" -v ./data:/data -e state_file=/data/people_identifier.json -e video_device="rtsp://<username>:<password>@<ip.ip.ip.ip>/<channel_number>" -e DISPLAY=docker.for.mac.localhost:0 -e enable_display=true twcbe/known_face_detector:master
```

All the above examples download the docker from docker hub. To build the image locally, run:
```bash
docker build -t known_face_detector .
```

To run using the local image, replace `twcbe/known_face_detector:master` in the above commands with `known_face_detector`.


To train new samples, make sure,
* the person stands in front of the camera
* the system is able to detect the face (probably recognized as `unknown`)
* inform the system, who is standing in front of the camera using the below command:
```
mosquitto_pub -m "{\"employee_id\":\"<SOME_UNIQUE_ID_OF_THE_PERSON>\", \"name\": \"<NAME_OF_THE_PERSON>\", \"add_current_person_detail\":true}" -t 'add_person_detail'
```
* Now, the logs should show the training happening, and statistics about the new dataset.
* Repeat the above command multiple times - at least 5 to 10 times.
* The system trains while it is live, so it can start recognizing the person during the training itself
* To reduce false positives, adjust the `MAX_DISTANCE_THRESHOLD` to 0.15 or slightly lower (default is 0.20)
```
docker ... -e MAX_DISTANCE_THRESHOLD=0.15 ...
```
