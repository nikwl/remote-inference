import cv2

from remote_inference.Streamer import Streamer

# Initiate the connection
s = Streamer()
s.connect(server_addr='localhost')

cap = cv2.VideoCapture(0)
while True:
    # Get an image, or multiple images
    _, frame = cap.read()

    # Send it (them)
    frame1, frame2 = frame, frame[:100, :100, 0]
    s.send_frame([frame1, frame2])

    # Get the processed frame
    frame1, frame2 = s.get_frame()

    # Show it (or save it)
    cv2.imshow('frame', frame1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break