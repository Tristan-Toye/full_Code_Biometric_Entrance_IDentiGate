broker_address = "192.168.137.21" # ip adress given by mobile hotspot
qos = 2
CHECK_DATABASE = "check_database"
RESPONSE_CHECK_DATABASE = "response_check_database"
VALIDATE_QR = "validate_QR"
RESPONSE_VALIDATE_QR = "response_validate_QR"
LOG_DATABASE = "log_database"
RESPONSE_LOG_DATABASE = "response_log_database"
SECURITY = "security"
FAILING_PATH = "failing"
ROLE_REQUEST_DATABASE = 'role_request_database'
RESPONSE_ROLE_REQUEST_DATABASE = 'response_role_request_database'
RESPONSE_VISITOR = 'response_visitor'
VISITOR = 'visitor'
REMOVED_USERS = 'removed_users'
LEAVING_QR = 'leaving_qr'
RESPONSE_LEAVING_QR = 'response_leaving_qr'
LIST_PATH = [RESPONSE_CHECK_DATABASE,RESPONSE_LOG_DATABASE,RESPONSE_VALIDATE_QR,RESPONSE_ROLE_REQUEST_DATABASE,RESPONSE_VISITOR,REMOVED_USERS,RESPONSE_LEAVING_QR]
LIST_CONNECT = [(path,qos) for path in LIST_PATH if path != FAILING_PATH]
LIST_CONNECT.append((FAILING_PATH,0))
failing_message = "UI failed"
SALT = bytes('''\xc2d>\x9a\xdf\x00\x13\x80\x98\xc4\xf0C\\\xc7&B\xa7:@H''', 'utf-8')

username = "CW2B2"
password = "KULeuven"
MQTT_SUCCES = 0

connection_params = {
    0 : "Connection successful",
    1: "Connection refused - incorrect protocol version",
    2: "Connection refused - invalid mqtt identifie",
    3: "Connection refused - server unavailable",
    4: "Connection refused - bad username or password" ,
    5: "Connection refused - not authorised 6-255: Currently unused.",
    'Min_delay': 5,
    'Max_delay': 80
}
