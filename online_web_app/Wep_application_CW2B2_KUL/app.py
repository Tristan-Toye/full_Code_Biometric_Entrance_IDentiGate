
from flask_info import app, socketio

if __name__ == "__main__":
    #print(app.root_path)
    socketio.run(app)
