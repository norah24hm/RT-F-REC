from flask import Flask, render_template, Response
import cv2
import numpy as np
import face_recognition
import os

app = Flask(__name__)
camera = cv2.VideoCapture(0)

# Load known faces
path = 'persons'
images = []
classNames = []
peopleList = os.listdir(path)

for cl in peopleList:
    curpeople = cv2.imread(f'{path}/{cl}')
    images.append(curpeople)
    classNames.append(os.path.splitext(cl)[0])  # remove the jpg
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print(encodeListKnown)
print('encoding complete ')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Resize frame for face detection
            height, width, _ = frame.shape
            imgS = cv2.resize(frame, (int(width * 0.25), int(height * 0.25)))
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Detect faces
            faceCurentFrame = face_recognition.face_locations(imgS)
            encodeCurentFrame = face_recognition.face_encodings(imgS, faceCurentFrame)

            for encodeFace, faceloc in zip(encodeCurentFrame, faceCurentFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    # print(name)
                    y1, x2, y2, x1 = faceloc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
                    cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            # Convert frame to JPEG and send to browser
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)