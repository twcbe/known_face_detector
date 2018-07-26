#!/bin/bash -el

git ls-files | xargs tar -cf - | ssh tw@10.137.125.215 bash -el -c "\"mkdir -p /home/tw/Projects/known_face_detector && rm -rf /home/tw/Projects/known_face_detector/* && cd /home/tw/Projects/known_face_detector && cat - | tar xf - && find ../ -type f -maxdepth 1 -exec cp {} ./ \; \""
