#!/bin/bash -el

git ls-files | xargs tar -cf - | ssh tw@tw-ubuntu-01.local bash -el -c "\"mkdir -p /home/tw/Projects/known_face_detector && rm -rf /home/tw/Projects/known_face_detector/* && cd /home/tw/Projects/known_face_detector && cat - | tar xf - &&  cp ../*.webm ./ \""
