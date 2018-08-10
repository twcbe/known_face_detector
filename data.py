import utils
import openface
import cv2
from face_detector import DlibFaceDetector
from image_processor import ImageProcessor
from threading import Thread
from utils import *

class Person(object):
    def __init__(self, employee_id, name = "", representations = []):
        self.name = name
        self.employee_id = employee_id
        self.representations = representations

    def add_representation(self, rep):
        self.representations.append(rep)

    def serialize(self):
        return {"name": self.name, "employee_id": self.employee_id}

    def __repr__(self):
        return "<{}: {} representations>".format(self.name, len(self.representations))

    def __str__(self):
        return self.__repr__()

class Dataset:
    def __init__(self, saved_state_file_path = None):
        self.saved_state_file_path = saved_state_file_path
        self.image_processor = ImageProcessor()
        self.on_data_change_handlers = []
        self.on_data_change(self.persist_state)
        print(">> Loading state_file from '%s'" % saved_state_file_path)
        self.known_people = self.load_saved_state(saved_state_file_path)
        print("number of entries in known_people dataset: {}".format(len(self.known_people)))
        print("known_people dataset: {}".format(self.known_people))

    def load_saved_state(self, saved_state_file_path):
        if saved_state_file_path is None:
            return []
        known_people_data = utils.load_file(saved_state_file_path) or []
        return [Person(person_data.get('employee_id'),
                       person_data.get('name'),
                       [np.array(rep) for rep in person_data.get('representations')]) for person_data in known_people_data]

    def persist_state(self):
        if self.saved_state_file_path is not None:
            print(">>> Saving known people dataset")
            print(">> updated number of entries in known_people dataset: {}".format(len(self.known_people)))
            print("known_people dataset: {}".format(self.known_people))
            known_people_data = [{"employee_id": person.employee_id,
                                  "name": person.name,
                                  "representations": [rep.tolist() for rep in person.representations]}
                                  for person in self.known_people]
            utils.save_file(known_people_data, self.saved_state_file_path)

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

    def create_or_get_person(self, employee_id):
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
        if image is None:
            return
        (_, _, rep) = self.image_processor.get_representation(image)
        self.add_representation(employee_id, rep)

    def add_person(self, employee_id, name=None):
        person = self.get_person(employee_id)
        if person is None:
            person = Person(employee_id, name)
            self.known_people.append(person)
        elif name is not None or name != "":
                person.name = name
        self.changed()
        return person

    def remove_person(self, employee_id):
        self.known_people = [person for person in self.known_people
                                    if person.employee_id != employee_id]

    def get_person(self, employee_id):
        employee_id_to_person_map = self.employee_id_to_person_map()
        if employee_id in employee_id_to_person_map:
            return employee_id_to_person_map[employee_id]
        return None

    def get_person_with_cluster_id(self, cluster_id):
        cluster_id_to_person_map = self.cluster_id_to_person_map()
        if cluster_id in cluster_id_to_person_map:
            return cluster_id_to_person_map[cluster_id]
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
    def __init__(self, dataset, messenger, current_image_lambda):
        self.messenger = messenger
        self.dataset = dataset
        self.current_image_lambda = current_image_lambda

    def listen(self):
        listen_to_thread = Thread(target=self.subscribe_to_add, args = ())
        listen_to_thread.daemon = True
        listen_to_thread.start()

    def subscribe_to_add(self):
        try:
            self.messenger.listen_to('add_person_detail', self.add_person_detail)
        except Exception as e:
            thread.interrupt_main()

    def add_person_detail(self, payload):
        if 'employee_id' not in payload:
            return
        employee_id = payload.get('employee_id')
        name = payload.get('name') # can be None or empty ""
        image = None
        representations=None
        if payload.get('add_current_person_detail'):
            image = self.current_image_lambda()
        else:
            representations = payload.get('representations') # can be None or empty []
            image = base64_to_image(payload.get('image')) # can be None

        self.dataset.add_person(employee_id, name)
        self.dataset.add_representations(employee_id, representations)
        self.dataset.add_representation_given_image(employee_id, image)
