import paho.mqtt.publish as publish
import paho.mqtt as mqtt
import json
from threading import Thread,Event

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

    def publish_message(self, payload):
        print(">> Publishing event to subscriber ====================================")
        topic = "face/known"
        # print(json.dumps(payload))
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
            print("publishing messages in background>>>>>>>>>>>>>")
            msgs=self.messages_to_publish
            self.messages_to_publish=[]
            for msg in msgs:
                self.publish_message(msg)
