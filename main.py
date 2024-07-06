import cv2
import numpy as np
import pandas as pd
import datetime

# Function to get the current timestamp in the video
def get_timestamp(cap):
    ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    return str(datetime.timedelta(milliseconds=ms))

# Function to track the balls and record events
def track_balls(video_path, output_video_path, output_text_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        return

    height, width, _ = frame.shape
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (width, height))
    
    # Create background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2()

    # Initialize list to store event records
    events = []

    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break

        fgmask = fgbg.apply(frame)
        _, fgmask = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)
        fgmask = cv2.erode(fgmask, None, iterations=2)
        fgmask = cv2.dilate(fgmask, None, iterations=2)

        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue

            (x, y, w, h) = cv2.boundingRect(contour)
            color = frame[y:y+h, x:x+w]
            color_mean = cv2.mean(color)[:3]

            ball_color = "Unknown"
            if color_mean[0] > 150 and color_mean[1] < 100 and color_mean[2] < 100:
                ball_color = "Blue"
            elif color_mean[0] < 100 and color_mean[1] > 150 and color_mean[2] < 100:
                ball_color = "Green"
            elif color_mean[0] < 100 and color_mean[1] < 100 and color_mean[2] > 150:
                ball_color = "Red"

            # Determine the quadrant
            quadrant = 0
            if x < width / 2 and y < height / 2:
                quadrant = 1
            elif x >= width / 2 and y < height / 2:
                quadrant = 2
            elif x < width / 2 and y >= height / 2:
                quadrant = 3
            elif x >= width / 2 and y >= height / 2:
                quadrant = 4

            timestamp = get_timestamp(cap)
            events.append([timestamp, quadrant, ball_color, "Entry"])

            cv2.putText(frame, f"Entry {ball_color} Ball - Q{quadrant}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        out.write(frame)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Save events to a text file
    df = pd.DataFrame(events, columns=["Time", "Quadrant Number", "Ball Colour", "Type"])
    df.to_csv(output_text_path, index=False)

# Define paths
video_path = 'input_video.mp4'  # Replace with the actual path to your downloaded video
output_video_path = 'output_video.avi'
output_text_path = 'events.txt'

# Run the tracking function
track_balls(video_path, output_video_path, output_text_path)
