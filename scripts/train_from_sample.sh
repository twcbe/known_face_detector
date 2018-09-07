#!/bin/bash -el

TRAINING_SAMPLES_FILE="./data/training_samples.json.log"
START_LINE=${1}
END_LINE=${2}
EMP_ID=${3}
USERNAME=${4}

if [ -z "$START_LINE" ] || [ -z "$END_LINE" ]; then
    echo "usage: $0 <START_LINE> <END_LINE> [<EMP_ID> <USERNAME>]"
    exit 1
fi

echo -e "line numbers: $START_LINE to $END_LINE \n"
sed -n "${START_LINE},${END_LINE}p;$(($END_LINE + 1))q" $TRAINING_SAMPLES_FILE | jq -sr '. | map(._time) | "start time: " + min, "end time:   " + max, "count: " + (length|tostring)'

echo -e "\nRecognized as..."
sed -n "${START_LINE},${END_LINE}p;$(($END_LINE + 1))q" $TRAINING_SAMPLES_FILE | jq -src '. | group_by(.closest_person.employee_id) | map(.[0].closest_person + {count: (.|length)})|sort_by(-.count)[]'

if [ -z "$USERNAME" ] || [ -z "$EMP_ID" ]; then
    echo "usage: $0 <START_LINE> <END_LINE> <EMP_ID> <USERNAME>"
    exit 0
fi

echo "sending training samples..."
sed -n "${START_LINE},${END_LINE}p;$(($END_LINE + 1))q" data/training_samples.json.log | jq --arg USERNAME "$USERNAME" --arg EMP_ID "$EMP_ID" -src '.|map(.rep as $rep | [{key: "name", value: $USERNAME},{key: "employee_id", value: $EMP_ID},{key: "add_current_person_detail", value: true},{key: "representation", value: []}] | from_entries | tojson+"\u0000")[]' | tr -d "\n" | xargs -0 -n1 mosquitto_pub -t add_person_detail -m
