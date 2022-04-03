import paho.mqtt.publish as publish
import time


MQTT_SERVER = "192.168.137.1"
MQTT_PATH = "test"
MQTT_PATH_2 = "test/test2"
FAILING_PATH = "failing"
failing_message = "raspberry pi failed"
username = "CW2B2"
password = "KULeuven"

will_parameter= {
    'topic':FAILING_PATH,
    'payload': failing_message

}
authorization_parameters = {
    'username': username,
    'password': password

}

def get_construct(topic,payload):
    MESSAGES_1 = {
        'topic': topic,
        'payload': payload,
        'qos': 2,
        'retain': False
    }
    return MESSAGES_1

while True:
    #publish.single(MQTT_PATH, "Hello World!", qos =2,hostname=MQTT_SERVER,client_id="sending_data",will= will_parameter,auth = authorization_parameters) # send data continuously every 3 seconds
    #publish.single(MQTT_PATH_2, "LOL", qos=2,hostname=MQTT_SERVER,client_id='sending_data_2',will=will_parameter,auth = authorization_parameters)  # send data continuously every 3 seconds
    msg = "hello world"
    msg_2 = 1234
    message_1 = get_construct(MQTT_PATH,msg)
    message_2 = get_construct(MQTT_PATH_2,msg_2)
    LIST_MESSAGES = [message_1, message_2]
    publish.multiple(LIST_MESSAGES, hostname=MQTT_SERVER, client_id="sending_data",
                   will=will_parameter, auth=authorization_parameters)
    time.sleep(3)