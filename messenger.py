import paho.mqtt
import json

mqtt_connection_details = {
    'host': 'm11.cloudmqtt.com',
    'port': 10833,
    'credentials': {
        'username': 'socnhliq',
        'password': '7wrIE_dxtWE6'
    }
}

class MqttMessenger(object):
    """docstring for MqttMessenger"""
    def __init__(self, arg):
        self.arg = arg

    def publish_message(payload):
        print(">> Publishing event to subscriber ====================================")
        mqtt.publish.single("face/known",
            payload = json.dumps(payload),
            hostname = mqtt_connection_details['host'],
            client_id = mqtt_connection_details['client_id'],
            auth = mqtt_connection_details['credentials'],
            port = mqtt_connection_details['port'],
            protocol = mqtt.client.MQTTv311)
