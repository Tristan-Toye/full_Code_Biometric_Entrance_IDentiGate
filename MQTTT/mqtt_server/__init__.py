import paho.mqtt.client as mqtt

from mqtt_server.constants import *

from mqtt_server.functions_db import *
client = mqtt.Client(MQTT_CLIENT_ID)             #create new instance
client.on_connect=on_connect  #bind call back function
client.on_disconnect = on_disconnect
client.on_subscribe=on_subscribe
client.username_pw_set(username,password=password)
client.will_set(FAILING_PATH,payload = failing_message)
client.reconnect_delay_set(min_delay=connection_params['Min_delay'],max_delay=connection_params['Max_delay'])
client.user_data_set(connection_params)
client.on_publish = on_publish
client.connect(broker_address)               #connect to broker

client.message_callback_add(CHECK_DATABASE,function_check_database)
client.message_callback_add(LOG_DATABASE,function_log_database)
client.message_callback_add(VALIDATE_QR, function_validate_QR)
client.message_callback_add(ROLE_REQUEST_DATABASE,function_role_request_database)
client.message_callback_add(VISITOR,function_visitor)
client.message_callback_add(LEAVING_QR,function_leaving_qr)
client.message_callback_add(COMPARE_DATABASES,function_compare_databases)
client.message_callback_add(VALIDATE_VISITOR_QR,function_validate_vistor_QR)