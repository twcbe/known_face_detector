import paho.mqtt.publish as publish
import paho.mqtt as mqtt
import json
from threading import Thread,Event
import json

mqtt_connection_details = {
    'host': 'm11.cloudmqtt.com',
    'port': 10833,
    'client_id': 'people_identifier',
    'credentials': {
        'username': 'socnhliq',
        'password': '7wrIE_dxtWE6'
    }
}

class MqttMessenger(object):
    def __init__(self):
        self.messages_to_publish = []
        self.event = Event()
        self.thread = Thread(target = self.background_publish_messages, args=())
        self.thread.daemon = True
        self.thread.start()

    def publish_message(self, payload, topic = "people_identifier/known_person_detected"):
        print(">> Publishing event")
        publish.single(topic,
            payload = json.dumps(payload),
            hostname = mqtt_connection_details['host'],
            client_id = mqtt_connection_details['client_id'],
            auth = mqtt_connection_details['credentials'],
            port = mqtt_connection_details['port'],
            protocol = mqtt.client.MQTTv311)

    def publish_message_async(self, payload):
        self.messages_to_publish.append(payload)
        self.event.set()

    def background_publish_messages(self):
        while True:
            self.event.wait()
            self.event.clear()
            (msgs, self.messages_to_publish) = (self.messages_to_publish, []) # use separate variable while publishing to reduce race conditions
            for msg in msgs:
                self.publish_message(msg)

    def listen_to(self, topic, callback_fn):
        client = mqtt.client.Client(mqtt_connection_details['client_id'])
        client.username_pw_set(mqtt_connection_details['credentials']['username'], mqtt_connection_details['credentials']['password'])
        client.on_connect = self.get_on_connect_handler(topic)
        client.on_message = self.get_callback(callback_fn)
        #client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pemtls_version=ssl.PROTOCOL_TLSv1_2)
        client.connect(host=mqtt_connection_details['host'], port=mqtt_connection_details['port'])
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