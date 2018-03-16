import utils
import openface
import cv2
from face_detector import DlibFaceDetector
from image_processor import ImageProcessor

class Person(dict):
    def __init__(self, employee_id, name=None):
        super({"name": name, "employee_id": employee_id}).__init__()
        self.name = name
        self.employee_id = employee_id
        self.cluster_id = cluster_id
        self.representations = []

    def add_representation(self, rep):
        self.representations.append(rep)

class Dataset:
    def __init__(self, saved_state_file_path = None):
        self.saved_state_file_path = saved_state_file_path
        self.known_people = [] if saved_state_file_path is None else utils.load_file(self.saved_state_file_path)
        self.image_processor = ImageProcessor()
        self.on_data_change_handlers = []
        self.on_data_change(self.persist_state)

    def persist_state(self):
        if saved_state_file_path is not None:
            utils.save_file(self.known_people, self.saved_state_file_path)

    def get_training_data(self):
        X=[] # representations
        Y=[] # cluster_ids
        for (cluster_id, person) in enumerate(self.known_people):
            for representation in person.representations:
                X.append(representation)
                Y.append(cluster_id)
        return (X, Y)

    def set_employee_details(self, employee_id, name):
        self.create_or_get_person(employee_id).name = name

    def create_or_get_person(employee_id):
        return self.get_person(employee_id) or self.add_person(employee_id)

    def add_representation(self, employee_id, representation):
        if representation is None:
            return
        self.create_or_get_person(employee_id).add_representation(representation)
        self.changed()

    def add_representations(self, employee_id, representations):
        if representations is None or representations == []:
            return
        person = self.create_or_get_person(employee_id)
        for representation in representations:
            person.add_representation(representation)
        self.changed()

    def add_representation_given_image(self, employee_id, image):
        rep = self.image_processor.get_representation(image)
        self.add_representation(employee_id, rep)

    def add_person(self, employee_id, name=None):
        person = self.get_person(employee_id)
        if person is None:
            person = Person(employee_id, name)
            self.known_people.append(person)
        if name is not None or name == "":
            set_employee_details(employee_id, name)
        return person

    def get_person(employee_id):
        employee_id_to_person_map = self.employee_id_to_person_map()
        if employee_id in employee_id_to_person_map:
            return employee_id_to_person_map[employee_id]
        return None

    def get_person_with_cluster_id(cluster_id):
        cluster_id_to_person_map = self.cluster_id_to_person_map()
        if employee_id in cluster_id_to_person_map:
            return cluster_id_to_person_map[employee_id]
        return None

    def employee_id_to_person_map(self):
        return {person.employee_id: person for cluster_id, person in enumerate(self.known_people)}

    def cluster_id_to_person_map(self):
        return {cluster_id: person for cluster_id, person in enumerate(self.known_people)}

    def on_data_change(self, callback_fn):
        self.on_data_change_handlers.append(callback_fn)

    def changed(self):
        for handler in self.on_data_change_handlers:
            handler()

class DataUpdater(object):
    def __init__(self, messenger, dataset):
        self.messenger = messenger
        self.dataset = dataset

    def listen(self):
        self.messenger.listen_to('add_person_detail', self.add_person_detail)

    def add_person_detail(self, payload):
        employee_id = payload['employee_id']
        name = payload['name'] # can be None or empty ""
        representations = payload['representations'] # can be None or empty []
        self.dataset.add_person(employee_id, name)
        self.dataset.add_representations(employee_id, representations)
