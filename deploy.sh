#!/bin/bash -el
DATE=$(date +"%Y%m%d%H%M%S")

ssh tw@10.137.125.215 bash -el -c "\"mkdir -p /home/tw/Projects/known_face_detector && cd /home/tw/Projects/known_face_detector && cp people_identifier.json ../people_identifier.json.production_$DATE.bak || echo 'first time deployment?' \""
scp tw@10.137.125.215:/home/tw/Projects/people_identifier.json.production_$DATE.bak ./ || echo 'first time deployment?'

git ls-files | xargs tar -cf - | ssh tw@10.137.125.215 bash -el -c "\"cd /home/tw/Projects/known_face_detector && rm -rf /home/tw/Projects/known_face_detector/* && cat - | tar xf - && cp ../people_identifier.json.production_$DATE.bak people_identifier.json\""
