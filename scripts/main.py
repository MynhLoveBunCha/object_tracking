# This code works on windows and linux
# Author: MINH DOAN
# Email: doannhatminh253@gmail.com

import numpy as np
import cv2
import sys
import serial


# functions
def CalculatePixelDistance(
    target: tuple[int, int], crosshair: tuple[int, int]
) -> tuple[int, int]:
    return crosshair[0] - target[0], crosshair[1] - target[1]


# init video capture object and serial port
camera_id = 2  # try 0, 1 or 2 if encounter errors
if "linux" in sys.platform:
    cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L)
    arduino = serial.Serial(
        port="/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_7583033343935150A092-if00",
        baudrate=115200,
        timeout=0,
    )
elif "win" in sys.platform:
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    arduino = serial.Serial(
        port="COM3",
        baudrate=115200,
        timeout=0,
    )

print("Initialization done!")

# FRAME setting
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
mid_frame = FRAME_WIDTH // 2, FRAME_HEIGHT // 2
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# init bounding box
bbox = (0, 0, 0, 0)  # x, y, w, h

# center of object
mid_x, mid_y = 0, 0

# colors dictionary
color_dict = {
    "red": (0, 0, 255),
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "yellow": (0, 255, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}

# main loop
while cap.isOpened():
    # get the webcam feed
    _, frame = cap.read()

    key = cv2.waitKey(5)
    if key == ord("q"):
        break
    elif key == ord("k"):
        # init tracker
        tracker = cv2.legacy.TrackerKCF_create()

        # init bounding box
        bbox = (0, 0, 0, 0)  # x, y, w, h

        # center of object
        mid_x, mid_y = 0, 0
        cv2.putText(
            frame,
            text="Select an object to track and then press SPACE to confirm!",
            org=(3, 15),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=color_dict["yellow"],
            thickness=1,
        )
        cv2.putText(
            frame,
            text="Press c to cancel!",
            org=(3, 30),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.5,
            color=color_dict["yellow"],
            thickness=1,
        )
        bbox = cv2.selectROI(
            windowName="Webcam Feed", img=frame, showCrosshair=True, fromCenter=False
        )
        cv2.destroyWindow("Webcam Feed")

    if bbox != (0, 0, 0, 0):
        tracker.init(frame, bbox)
        ok, bbox = tracker.update(frame)
        bbox = tuple(map(int, bbox))
        if ok:
            # calculate errors
            mid_x = bbox[0] + int(bbox[2] / 2)
            mid_y = bbox[1] + int(bbox[3] / 2)
            x_diff, y_diff = CalculatePixelDistance((mid_x, mid_y), mid_frame)

            # transmit error to arduino
            arduino.write(f"{x_diff}".encode("utf-8"))

            # display bounding box
            cv2.rectangle(
                frame,
                (bbox[0], bbox[1]),
                (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                color_dict["red"],
                3,
            )
            cv2.line(
                frame,
                (mid_x, bbox[1] + bbox[3] // 3),
                (mid_x, bbox[1] + bbox[3] - bbox[3] // 3),
                color_dict["blue"],
                2,
            )  # vertical
            cv2.line(
                frame,
                (bbox[0] + bbox[2] // 3, mid_y),
                (bbox[0] + bbox[2] - bbox[2] // 3, mid_y),
                color_dict["blue"],
                2,
            )  # horizontal
            cv2.putText(
                frame,
                text=f"Horizontal Error: {x_diff}",
                org=(3, FRAME_HEIGHT - 3),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.75,
                color=color_dict["blue"],
                thickness=2,
            )
            cv2.putText(
                frame,
                text=f"Vertical Error: {y_diff}",
                org=(3, FRAME_HEIGHT - 18),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.75,
                color=color_dict["blue"],
                thickness=2,
            )
        else:
            # reset bounding box
            bbox = (0, 0, 0, 0)  # x, y, w, h

            # reset center of object
            mid_x, mid_y = 0, 0

    # instruction
    cv2.putText(
        frame,
        text="Press k to select object to track!",
        org=(3, 15),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.5,
        color=color_dict["yellow"],
        thickness=1,
    )
    cv2.putText(
        frame,
        text="Press q to exit!",
        org=(3, 30),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.5,
        color=color_dict["yellow"],
        thickness=1,
    )

    # draw frame crosshair
    cv2.line(
        frame,
        (mid_frame[0], FRAME_HEIGHT // 3),
        (mid_frame[0], FRAME_HEIGHT - FRAME_HEIGHT // 3),
        color_dict["green"],
        2,
    )  # vertical
    cv2.line(
        frame,
        (FRAME_WIDTH // 3, mid_frame[1]),
        (FRAME_WIDTH - FRAME_WIDTH // 3, mid_frame[1]),
        color_dict["green"],
        2,
    )  # horizontal
    cv2.imshow("Webcam Feed", frame)

cap.release()
cv2.destroyAllWindows()
