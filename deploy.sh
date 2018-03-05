#!/bin/bash -el

git archive --format=tar HEAD | ssh tw@tw-ubuntu-01.local bash -xel -c "\"mkdir -p /home/tw/Projects/known_face_detector && rm -rf /home/tw/Projects/known_face_detector/* && cat - | tar xf - -C /home/tw/Projects/known_face_detector\""
