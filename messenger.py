import paho.mqtt.publish as publish
import paho.mqtt as mqtt
import json
from threading import Thread,Event
from utils import *

class MqttMessenger(object):
    def __init__(self, host, port, client_id, username, password, topic, source_name):
        self.mqtt_host = host
        self.mqtt_port = port
        self.mqtt_client_id = client_id
        self.mqtt_username = username
        self.mqtt_password = password
        self.mqtt_topic = topic
        self.source_name = source_name
        self.messages_to_publish = []
        self.event = Event()
        self.thread = Thread(target = thread_callback(self.background_publish_messages), args=())
        self.thread.daemon = True
        self.thread.start()

    def publish_message(self, payload, topic = "people_identifier/known_person_detected"):
        print(">> Publishing event")
        publish.single(topic,
            payload = json.dumps(payload),
            hostname = self.mqtt_host,
            client_id = self.mqtt_client_id,
            auth = {'username': self.mqtt_username, 'password': self.mqtt_password},
            port = self.mqtt_port,
            protocol = mqtt.client.MQTTv311)

    def publish_message_async(self, payload):
        payload = payload.copy()
        payload['source'] = self.source_name
        self.messages_to_publish.append(payload)
        self.event.set()

    def background_publish_messages(self):
        while True:
            self.event.wait()
            self.event.clear()
            (msgs, self.messages_to_publish) = (self.messages_to_publish, []) # use separate variable while publishing to reduce race conditions
            for msg in msgs:
                self.publish_message(msg, self.mqtt_topic)

    def listen_to(self, topic, callback_fn):
        client = mqtt.client.Client(self.mqtt_client_id)
        client.username_pw_set(self.mqtt_username, self.mqtt_password)
        client.on_connect = self.get_on_connect_handler(topic)
        client.on_message = self.get_callback(callback_fn)
        #client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pemtls_version=ssl.PROTOCOL_TLSv1_2)
        client.connect(host=self.mqtt_host, port=self.mqtt_port)
        client.loop_forever()

    def get_on_connect_handler(self, topic):
        def on_connect(client, userdata, flags, rc):
            client.subscribe(topic=topic, qos=2)
        return on_connect


    def get_callback(self, callback_fn):
        def on_message_callback(client, userdata, message):
            message = json.loads(message.payload)
            callback_fn(message)
        return on_message_callback
