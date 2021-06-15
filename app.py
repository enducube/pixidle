"""
pixidle by enducube/Jack Milner
"""
import os
from app import socketio, app

if __name__ == "__main__":
    print("bar")
    print(os.getcwd())
    socketio.run(app,host='0.0.0.0',port=80)
