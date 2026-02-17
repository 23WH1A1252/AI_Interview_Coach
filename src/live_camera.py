import cv2
import av
from streamlit_webrtc import VideoTransformerBase

class FaceDetector(VideoTransformerBase):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.face_detected = False

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            self.face_detected = True
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        else:
            self.face_detected = False

        return img
