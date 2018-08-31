# face-recognition-workspace

[![CircleCI](https://circleci.com/gh/twlabs/face-recognition-workspace.svg?style=svg&circle-token=a7216b8a8bcb8065391871ca619301bcbefcda75)](https://circleci.com/gh/twlabs/face-recognition-workspace)

This program is easier to setup on a linux machine using docker and a camera attached to the system. There are several customizable options detailed below. To quickly get started jump to the getting started section below.

On OSX only network cameras are supported.

The program can be run in headless mode or with display attached. The display shows the recognized person visually. In case the system doesn't recognize a person correctly it will show the next closest matching person in paranthesis - this is not a match, just shown for debugging.

* enable or disable display: `-e enable_display=true` (default false, ie. headless)

* The following flags specify to store the state file containing people identities in ./data/people_identifier.json file.
`-v ./data:/data -e state_file=/data/people_identifier.json`

The source of the video feed can be anything that opencv supports as video source! It could be a camera attached to the computer, a network camera reachable using an rtsp URI, a pre-recorded video file at a given path.

* To specify the source:
`-e video_device=-1 --device /dev/video0` choose the first camera attached to the machine
`-e video_device=-1 --device /dev/video1` choose the second camera attached to the machine
`-e video_device="rtsp://<username>:<password>@<ip>/<channel_number>"` choose a network camera reachable using the given URI. Make sure to enter the username, password, ip and channel_number.
`-e video_device="/data/video_filename.mp4"` make sure to put the video file in the `./data` folder

## Linux:
### Prerequisites:
* docker
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
DISPLAY=:0 xhost +  # enable remote connections to XServer
docker run -it --rm --name="known_face_detector" -v ./data:/data --device /dev/video0 -e enable_display=true --net=host --ipc=host -v /tmp/X11-unix:/tmp/X11-unix -e DISPLAY=:0 -e video_device=-1 -e state_file=/data/people_identifier.json twcbe/known_face_detector:master
```

## OSX:
### Prerequisites:
* docker
* xquartz - for displaying video on screen, not necessary for headless mode.
* network camera - required, since OSX does not provide a raw video device, it cannot be forwarded inside the container. One can run the program like a demo using a pre-captured video file too, in which case the network camera is not necessary.

### Getting Started:
Run the detector in headless mode with network camera: (no need to clone this repo)
```bash
mkdir data
docker run -it --rm --name="known_face_detector" -v ./data:/data -e state_file=/data/people_identifier.json -e video_device="rtsp://<username>:<password>@<ip.ip.ip.ip>/<channel_number>" twcbe/known_face_detector:master
```

All the above examples download the docker from docker hub. To build the image locally, run:
```bash
docker build -t known_face_detector .
```

To run using the local image, replace `twcbe/known_face_detector:master` in the above commands with `known_face_detector`
