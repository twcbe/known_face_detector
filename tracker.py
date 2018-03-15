import json
from messenger import MqttMessenger

MIN_NUMBER_OF_OCCURENCES = 3
MAX_NUMBER_OF_FRAMES_TO_PROCESS = 20 

class Tracker(object):
     """docstring for Tracker"""
     def __init__(self, messenger_class = MqttMessenger):
         super(Tracker, self).__init__()
         self.frames = []
         self.classes_detected_in_past_frames = []
         self.event_raised_in_past_frames = []
         self.messenger = messenger_class()

    def update(self, face_detections_this_frame):
        self.frames.append(face_detections_this_frame)
        self.frames = self.frames[-MAX_NUMBER_OF_FRAMES_TO_PROCESS:]

        classes_detected_this_frame = set([detection['class'] for detection in face_detections_this_frame])
        self.classes_detected_in_past_frames.append(classes_detected_this_frame)
        self.classes_detected_in_past_frames = self.classes_detected_in_past_frames[-MAX_NUMBER_OF_FRAMES_TO_PROCESS]

        event_raised_this_frame = set()
        for detection in face_detections_this_frame:
            detected_class = detection['class']
            if is_a_valid_recognition_event():
                event_raised_this_frame.add(detected_class)
                self.raise_event(detection)

        self.event_raised_in_past_frames.append(event_raised_this_frame)
        self.event_raised_in_past_frames = self.event_raised_in_past_frames[-MIN_NUMBER_OF_MISSES]

    def is_a_valid_recognition_event(self):
        # N = MIN_NUMBER_OF_OCCURENCES
        # M = MIN_NUMBER_OF_MISSES
        # to raise recognition event: (a person...)
        # - should be recognized in atleast past N consecutive frames
        recognized_in_all_past_n_frames = all(detected_class in recognized_classes for recognized_classes in self.get_past_n_frame_detections())
        # - should not be part of a raised event in atleast past M frames
        raised_in_any_past_m_frames = any(detected_class in raised_classes for raised_classes in self.get_past_m_frame_events())
        return recognized_in_all_past_n_frames and not raised_in_any_past_m_frames:

    def raise_event(self, detection):
        self.messenger.publish_message(detection)

    def get_past_n_frame_detections(self):
        return self.get_last_n(classes_detected_in_past_frames, MIN_NUMBER_OF_OCCURENCES)

    def get_past_m_frame_events(self):
        return self.get_last_n(event_raised_in_past_frames, MIN_NUMBER_OF_MISSES)

    def get_last_n(self, array, n):
        return array[-n:]

