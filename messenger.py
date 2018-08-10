import paho.mqtt.publish as publish
import paho.mqtt as mqtt
import json
from threading import Thread,Event
from utils import get_settings
import json

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
            hostname = get_settings()['mqtt']['host'],
            client_id = get_settings()['mqtt']['client_id'],
            auth = get_settings()['mqtt']['credentials'],
            port = get_settings()['mqtt']['port'],
            protocol = mqtt.client.MQTTv311)

    def publish_message_async(self, payload):
        payload = payload.copy()
        payload['source'] = get_settings()['source_name']
        self.messages_to_publish.append(payload)
        self.event.set()

    def background_publish_messages(self):
        try:
            while True:
                self.event.wait()
                self.event.clear()
                (msgs, self.messages_to_publish) = (self.messages_to_publish, []) # use separate variable while publishing to reduce race conditions
                for msg in msgs:
                    self.publish_message(msg, get_settings()['mqtt']['topic'])
        except Exception as e:
            thread.interrupt_main()

    def listen_to(self, topic, callback_fn):
        client = mqtt.client.Client(get_settings()['mqtt']['client_id'])
        client.username_pw_set(get_settings()['mqtt']['credentials']['username'], get_settings()['mqtt']['credentials']['password'])
        client.on_connect = self.get_on_connect_handler(topic)
        client.on_message = self.get_callback(callback_fn)
        #client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pemtls_version=ssl.PROTOCOL_TLSv1_2)
        client.connect(host=get_settings()['mqtt']['host'], port=get_settings()['mqtt']['port'])
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
