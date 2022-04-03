from mqtt_server import client

if __name__ == '__main__':
    while True:
        client.loop_forever()
        """
        user = session_db.query(User).filter_by(username='Tristan Toye').first()
        print(user.username)
        print(user.roles[0].name)
        """
