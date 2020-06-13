# remote-inference
## Overview
This is a super simple and lightweight imagezmq wrapper that allows you to do inference using multiple images on a server remotely. 

An integral part of testing and deploying a computer vision algorithm is testing its performance on real data, often on live video. However if you do most of your work on a server and are working from a laptop or non-gpu equipped desktop, this often isn't possible. This wrapper enables easy integration of fast two way video streaming into existing algorithms. Simply start the video streamer script on the remote side and replace the lines where you would collect and display images on the server side  to equip your existing algorithm with high speed remote inference capabilities.

## Installation

3) Install required python packages:
    ```bash
    pip install -r requirements.txt
    ``` 
4) Test installation, run these in two seperate terminals:
    ```bash
    python test_client.py

    python test_server.py
    ```

## Usage
Client side:
```python
import cv2

from remote_inference.Streamer import Streamer

# Initiate the connection
s = Streamer(client_addr='localhost')
s.connect()

cap = cv2.VideoCapture(0)
while True:
    # Get an image, or multiple images
    _, frame = cap.read()

    # Send them
    frame1, frame2 = frame, frame[:100, :100, 0]
    s.send_frame([frame1, frame2])

    # Get the result
    frame_infered = s.get_frame()

    # Show it (or save it)
    cv2.imshow('frame', frame_infered)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

Server side:
```python
import cv2

from remote_inference.Streamer import Streamer

# Your cv algorithm
from somecv_algorithm import infer

# Initiate the connection
s = Streamer()
s.accept()

while True:
    # Get the frame(s)
    frame1, frame2 = s.get_frame()

    # Infer
    frame_infered = infer(frame1, frame2)

    # Send the result
    s.send_frame(frame_infered)

```