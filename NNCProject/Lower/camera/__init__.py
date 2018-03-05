import cv2
import pickle
from threading import Thread, Lock


camera = cv2.VideoCapture(0)
frame_bytes = None
write_lock = Lock()


def start_collect_image(lock, cam):
    global frame_bytes
    while True:
        ret, frame = cam.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame = cv2.resize(frame, (0, 0), fx=0.04, fy=0.04, interpolation=cv2.INTER_AREA)
        b = pickle.dumps(frame, protocol=3)
        with lock:
            frame_bytes = b


def get_frame():
    global frame_bytes
    global write_lock
    with write_lock:
        return frame_bytes


def get_frame_size():
    ret, f = camera.read()
    f = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
    f = cv2.resize(f, (0, 0), fx=0.04, fy=0.04, interpolation=cv2.INTER_AREA)
    b = pickle.dumps(f, protocol=3)
    return len(b)


thread = Thread(target=start_collect_image, args=(write_lock, camera))
thread.start()
