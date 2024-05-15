
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('image_data')
def handle_image_data(image_bytes):
    print("Received image data:", len(image_bytes), "bytes")

@socketio.on('test_data')
def handle_test_data(test_data):
    print("Received test data:", len(test_data), "bytes")



@app.route('/')
def hello_world():
    return 'Hello, Worldddyyy!'




if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=8080, debug=True)
