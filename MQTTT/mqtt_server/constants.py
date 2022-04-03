from sqlalchemy.ext.declarative import declarative_base


base_db = declarative_base()
db_string = "postgresql://wtdjzngqqcdejo:816569dfc06e2457582ec73f6f43e576e57cb3aa1c1f915466afd4f3e7936a5a@ec2-34-242-89-204.eu-west-1.compute.amazonaws.com:5432/dc3lnlv8ph2q1i"


#broker_address = "192.168.137.17" # ip adress given by mobile hotspot
MQTT_CLIENT_ID="recieving_data"
broker_address = 'localhost'
qos = 2
CHECK_DATABASE = "check_database"
RESPONSE_CHECK_DATABASE = "response_check_database"
VALIDATE_QR = "validate_QR"
VALIDATE_VISITOR_QR = "validate_visitor_QR"
RESPONSE_VALIDATE_QR = "response_validate_QR"
LOG_DATABASE = "log_database"
RESPONSE_LOG_DATABASE="response_log_database"
ROLE_REQUEST_DATABASE = 'role_request_database'
RESPONSE_ROLE_REQUEST_DATABASE = 'response_role_request_database'
VISITOR ='visitor'
RESPONSE_VISITOR = 'response_visitor'
SECURITY = "security"
FAILING_PATH = "failing"
LEAVING_QR = "leaving_qr"
RESPONSE_LEAVING_QR = "response_leaving_qr"
COMPARE_DATABASES = 'compare_databases'
RESPONSE_COMPARE_DATABASES = 'response_compare_databases'
SALT = bytes('''\xc2d>\x9a\xdf\x00\x13\x80\x98\xc4\xf0C\\\xc7&B\xa7:@H''', 'utf-8')
LIST_PATH = [CHECK_DATABASE,LOG_DATABASE,FAILING_PATH,VALIDATE_QR,SECURITY,ROLE_REQUEST_DATABASE,VISITOR,LEAVING_QR,COMPARE_DATABASES,VALIDATE_VISITOR_QR]
LIST_CONNECT = [(path,qos) for path in LIST_PATH if path != FAILING_PATH]
LIST_CONNECT.append((FAILING_PATH,0))
failing_message = "server failed"

username = "CW2B2"
password = "KULeuven"
MQTT_SUCCES = 0

connection_params = {
    0 : "Connection successful",
    1: "Connection refused - incorrect protocol version",
    2: "Connection refused - invalid client identifie",
    3: "Connection refused - server unavailable",
    4: "Connection refused - bad username or password" ,
    5: "Connection refused - not authorised 6-255: Currently unused.",
    'Min_delay': 5,
    'Max_delay': 80
}