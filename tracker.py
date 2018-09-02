from messenger import MqttMessenger
from utils import filter_keys


class Tracker(object):
    """docstring for Tracker"""
    def __init__(self, messenger = None, MIN_NUMBER_OF_OCCURENCES = 3, MAX_NUMBER_OF_FRAMES_TO_PROCESS = 20, MIN_NUMBER_OF_MISSES = 50, enable_events = False):
        super(Tracker, self).__init__()
        self.MIN_NUMBER_OF_OCCURENCES = MIN_NUMBER_OF_OCCURENCES
        self.MAX_NUMBER_OF_FRAMES_TO_PROCESS = MAX_NUMBER_OF_FRAMES_TO_PROCESS  # just buffer size. should be greater than or equal to MIN_NUMBER_OF_OCCURENCES
        self.MIN_NUMBER_OF_MISSES = MIN_NUMBER_OF_MISSES
        self.classes_detected_in_past_frames = []
        self.people_seen_in_past_frames = []
        self.messenger = messenger
        self.enable_events = enable_events

    def update(self, face_detections_this_frame):
        classes_detected_this_frame = set([self.get_id(detection) for detection in face_detections_this_frame])
        self.classes_detected_in_past_frames.append(classes_detected_this_frame)
        self.classes_detected_in_past_frames = self.get_last_n(self.classes_detected_in_past_frames, self.MAX_NUMBER_OF_FRAMES_TO_PROCESS)

        people_seen_this_frame = set()
        for detection in face_detections_this_frame:
            print(filter_keys(detection, ['known','distance','closest_matching_person','predicted_person']))
            detected_class = self.get_id(detection)
            if detected_class is None:
                continue
            (is_valid_recognition_event, event_recently_raised) = self.check_recognition_event(detected_class)
            if is_valid_recognition_event:
                self.raise_event(detection['predicted_person'])
                people_seen_this_frame.add(detected_class)
            if event_recently_raised:
                people_seen_this_frame.add(detected_class)
                detection['event_raised']=True
        self.people_seen_in_past_frames.append(people_seen_this_frame)
        self.people_seen_in_past_frames = self.get_last_n(self.people_seen_in_past_frames, self.MIN_NUMBER_OF_MISSES)



    def get_id(self, detection):
        if detection['predicted_person'] is None:
            return None
        return detection['predicted_person']['employee_id']

    def check_recognition_event(self, detected_class):
        # N = MIN_NUMBER_OF_OCCURENCES
        # M = MIN_NUMBER_OF_MISSES
        # to raise recognition event: (a person...)
        # - should be recognized in atleast past N consecutive frames
        recognized_in_all_past_n_frames = all(detected_class in recognized_classes for recognized_classes in self.get_past_n_frame_detections())
        # - should not be part of a raised event in atleast past M frames
        raised_in_any_past_m_frames = any(detected_class in raised_classes for raised_classes in self.get_past_m_frame_events())
        is_valid_recognition_event = recognized_in_all_past_n_frames and not raised_in_any_past_m_frames
        event_recently_raised = recognized_in_all_past_n_frames and raised_in_any_past_m_frames
        return (is_valid_recognition_event, event_recently_raised)

    def raise_event(self, detection):
        if self.enable_events and self.messenger:
            self.messenger.publish_message_async(detection)

    def get_past_n_frame_detections(self):
        return self.get_last_n(self.classes_detected_in_past_frames, self.MIN_NUMBER_OF_OCCURENCES)

    def get_past_m_frame_events(self):
        return self.get_last_n(self.people_seen_in_past_frames, self.MIN_NUMBER_OF_MISSES)

    def get_last_n(self, array, n):
        return array[-n:]

