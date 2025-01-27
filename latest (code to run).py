#!/usr/bin/env python

from __future__ import print_function  # Python 2/3 compatibility

import datetime
import cv2  # Import the OpenCV library
import numpy as np  # Import Numpy library

def main():
    """
    Main method of the program.
    """

    # Create a VideoCapture object
    cap = cv2.VideoCapture(1)

    # Create the background subtractor object
    # Use the last 700 video frames to build the background
    back_sub = cv2.createBackgroundSubtractorMOG2(history=700,
                                                  varThreshold=25, detectShadows=True)

    # Create kernel for morphological operation
    # You can tweak the dimensions of the kernel
    # e.g. instead of 20,20 you can try 30,30.
    kernel = np.ones((20, 20), np.uint8)

    while True:

        # Capture frame-by-frame
        # This method returns True/False as well
        # as the video frame.
        ret, frame = cap.read()

        # Use every frame to calculate the foreground mask and update
        # the background
        fg_mask = back_sub.apply(frame)

        # Close dark gaps in foreground object using closing
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        # Remove salt and pepper noise with a median filter
        fg_mask = cv2.medianBlur(fg_mask, 5)

        # Threshold the image to make it either black or white
        _, fg_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)

        # Find the index of the largest contour and draw bounding box
        fg_mask_bb = fg_mask
        contours, hierarchy = cv2.findContours(fg_mask_bb, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        areas = [cv2.contourArea(c) for c in contours]

        # If there are no countours
        if len(areas) < 1:

            # Display the resulting frame
            cv2.imshow('frame', frame)

            # If "q" is pressed on the keyboard,
            # exit this loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Go to the top of the while loop
            continue

        else:
            # Find the largest moving object in the image
            max_index = np.argmax(areas)

        # Draw the bounding box
        cnt = contours[max_index]
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Draw circle in the center of the bounding box
        x2 = x + int(w / 2)
        y2 = y + int(h / 2)
        cv2.circle(frame, (x2, y2), 4, (0, 255, 0), -1)

        # Print the centroid coordinates (we'll use the center of the
        # bounding box) on the image
        text = "x: " + str(x2) + ", y: " + str(y2)
        cv2.putText(frame, text, (x2 - 10, y2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('frame', frame)

        # If "q" is pressed on the keyboard,
        # exit this loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # Draw a line down the center of the image
        cv2.line(frame, (int(frame.shape[1] / 2), 0),
                 (int(frame.shape[1] / 2), frame.shape[0]), (0, 255, 0), 2)

        count = 0

        # Increase counter when someone crosses the center line
        if x2 > int(frame.shape[1] / 2):
            count += 1
            with open("output.csv", "a") as f:
                print("ID:", count, 'crossed going in', datetime.datetime.now(), file=f)
        
        # Decrease counter when someone crosses the center line
        if x2 < int(frame.shape[1] / 2):
            if count <= 1:
                count = 0
            elif count >= 1:
                count -= 1
            with open("output.csv", "a") as f:
                print("ID:", count, 'crossed going out at', datetime.datetime.now(), file=f)

        # Show number of people crossing the center line
        cv2.putText(frame, "Current Occupancy " + str(count), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('frame', frame)

        # If "q" is pressed on the keyboard,
        # exit this loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close down the video stream
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print(__doc__)
    main()
