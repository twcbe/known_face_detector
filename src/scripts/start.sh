#!/bin/bash -el

ENV=${1:-development}

# for interactive shell:
# docker run -v /home/tw/Projects/known_face_detector:/known_face_detector --net=host --ipc=host -v /tmp/X11-unix:/tmp/X11-unix -e DISPLAY=:0 --device /dev/video1 -p 9000:9000 -p 8000:8000 -it openface /bin/bash -c "cd /known_face_detector; bash"

# for running the container:
docker run -v /home/tw/Projects/known_face_detector:/known_face_detector --net=host --ipc=host -v /tmp/X11-unix:/tmp/X11-unix -e DISPLAY=:0 -p 9000:9000 -p 8000:8000 -it openface /bin/bash -c "cd /known_face_detector; ENV=$ENV python main.py"
