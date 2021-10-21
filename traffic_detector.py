
import argparse

ag = argparse.ArgumentParser()
ag.add_argument("-x", "--xml", required=True,
                help="path to  xml file")
ag.add_argument("-v", "--video", required=True,
                help="path to video")
args = vars(ag.parse_args())

# OpenCV Python program to detect cars in video frame
import cv2
# capture frames from a video
cap = cv2.VideoCapture(args["video"])

# Trained XML classifiers describes some features of some object we want to detect
car_cascade = cv2.CascadeClassifier(args["xml"])

# loop runs if capturing has been initialized.
while True:
    # reads frames from a video
    ret, frames = cap.read()
    frames = cv2.resize(frames, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_LINEAR)
    # convert to gray scale of each frames
    gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)
    # Detects cars of different sizes in the input image
    cars = car_cascade.detectMultiScale(gray, 1.1, 1)
    # To draw a rectangle in each cars
    for (x, y, w, h) in cars:
        cv2.rectangle(frames, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # Display frames in a window
        cv2.imshow('Car Detection', frames)
    # Wait for Enter key to stop
    if cv2.waitKey(33) == 13:
        break

cv2.destroyAllWindows()
