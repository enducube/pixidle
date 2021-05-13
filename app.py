"""
pixidle by enducube/Jack Milner
"""

from app import socketio, app

if __name__ == "__main__":
    print("bar")
    socketio.run(app,host='0.0.0.0')
