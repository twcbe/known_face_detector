import utils
import openface
import cv2
from face_detector import DlibFaceDetector
from image_processor import ImageProcessor

class Person(dict):
    def __init__(self, employee_id, name):
        super({"name": name, "employee_id": employee_id}).__init__()
        self.name = name
        self.employee_id = employee_id
        self.cluster_id = cluster_id
        self.representations = []

    def add_representation(self, rep):
        self.representations.append(rep)

class Dataset:
    def __init__(self):
        self.known_people = [] # [Person, Person]
        self.image_processor = ImageProcessor()
        # if(utils.exists("dataset")):
        #     self.data = utils.load_file("dataset")

    def get_training_data(self):
        X=[] # representations
        Y=[] # cluster_ids
        for (cluster_id, person) in enumerate(self.known_people):
            for representation in person.representations:
                X.append(representation)
                Y.append(cluster_id)
        return (X, Y)

    def create_or_get_person(employee_id):
        return self.get_person(employee_id) or self.add_person(employee_id)

    def add_entry(self, employee_id, rep):
        if rep is None:
            return
        self.create_or_get_person(employee_id).add_representation(rep)

    def add_entry_given_image(self, employee_id, image):
        rep = self.image_processor.get_representation(image)
        self.add_entry(employee_id, rep)

    def set_employee_details(self, employee_id, name):
        self.create_or_get_person(employee_id).name = name

    def add_person(self, employee_id, name=None):
        person = self.get_person(employee_id)
        if person is None:
            person = Person(employee_id, name)
            self.known_people.append(person)
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
