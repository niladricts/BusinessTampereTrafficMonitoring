import cv2
# https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
# face haar cascade detection
face_cascade = cv2.CascadeClassifier("C:\\Users\\bsens\\face.xml")
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("C:\\Users\\bsens\\Street - 19627.mp4")
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2BGRA)

    # faces multiscale detector
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # loop throughout the object detected and place a rectangle around it
    for (x, y, w, h) in faces:
        # put a rectangle around the object/face when detected
        gray = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(gray, "FACE", (x, y - 10), font, 0.5, (11, 255, 255), 2, cv2.LINE_AA)
        roi_gray = gray[y:y + h, x:x + w]

    # Display the resulting frame
    cv2.imshow("black and white", gray)
    if cv2.waitKey(1) and 0xFF == ord("q"):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
