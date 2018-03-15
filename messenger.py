import paho.mqtt.publish as publish
import paho.mqtt as mqtt
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
    def publish_message(self, payload):
        print(">> Publishing event to subscriber ====================================")
        topic = "face/known"
        publish.single(topic,
            payload = json.dumps(payload),
            hostname = mqtt_connection_details['host'],
            client_id = mqtt_connection_details['client_id'],
            auth = mqtt_connection_details['credentials'],
            port = mqtt_connection_details['port'],
            protocol = mqtt.client.MQTTv311)
