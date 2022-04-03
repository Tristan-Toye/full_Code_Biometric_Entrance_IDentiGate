from flask import url_for

PRE_URL_STRING = 'https://identigate.herokuapp.com'
secret_key_pyotp = 'JD2E34VPNRYGWID3O7LDVSUTM6R66MUX'
max_attempts_google_auth=3
min_attempts_password_before_notification = 2
max_attempts_password = 5
# qr_code
time_interval = 43200
kenteken = "}"

MODEL = 'hog'
TOLERANCE = 0.6

SALT = bytes('''\xc2d>\x9a\xdf\x00\x13\x80\x98\xc4\xf0C\\\xc7&B\xa7:@H''', 'utf-8')
cutoff_hash = 32
