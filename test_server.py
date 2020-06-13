import cv2

from remote_inference.Streamer import Streamer

# Initiate the connection
s = Streamer()
s.accept(client_addr='localhost')

while True:
    # Get the frame(s)
    frame1, frame2 = s.get_frame()

    # do something

    # Send the result
    s.send_frame([frame1, frame2])
