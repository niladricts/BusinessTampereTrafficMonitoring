import cv2


def car_detection():
    """
    Method to detect car objects from the traffic video
    """
    car_classification = cv2.CascadeClassifier("haarcascade_car.xml")
    capt = cv2.VideoCapture("MVI_6838.mp4")
    # looping through each frame

    while True:
        ret, frame = capt.read()
        # Resizing the frame as it takes whole screen of PC
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        # gray scale conversion to detect objects
        gray_version = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Tuning classification parameters for better detection
        cars = car_classification.detectMultiScale(gray_version, 1.4, 6)
        for (x, y, w, h) in cars:
            # putting boundary boxes around the detected cars
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(gray_version, "CAR", (x, y - 10), font, 0.5, (11, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Cars', frame)
        if cv2.waitKey(1) == 13:  # for enter
            break
    capt.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    car_detection()
