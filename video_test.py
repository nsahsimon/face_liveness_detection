import cv2
import numpy as np
from tester import test

# Function to perform face detection and classification
def classify_frame(frame):
    # Placeholder function for face detection and classification
    # Replace this with your actual implementation
    result = test(frame)
    # return (1, 0.8, (50, 50, 100, 100))  # (label, confidence, bounding box)
    return result  # (label, confidence, bounding box)

# Function to write text on frame
def write_text(frame, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, frame.shape[0] - 10)
    fontScale = 1
    fontColor = (255, 255, 255)
    lineType = 2

    cv2.putText(frame, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

def write_header(frame):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 25)
    fontScale = 1
    fontColor = (255, 255, 255)
    lineType = 2

    cv2.putText(frame, "Antispoof - Jamie York", (10, 20), font, fontScale, fontColor, lineType)

# Read video from directory
video_path = 'test_video.mp4'
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Could not open video")
    exit()

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
output_path = 'output.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (480, 640))
text = None
bbox = None
# Read and process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Process only 1 frame per second
    if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % int(fps) == 0:
        label, confidence, bbox = classify_frame(frame)

        # Draw bounding box on frame
        if label == 1:
            color = (0, 255, 0)  # Green for real face
        else:
            color = (0, 0, 255)  # Red for fake face
        
        # Write label and confidence on frame
        if confidence >= 0.6:
            text = f"Face: {'Real' if label == 1 else 'Fake'}, Confidence: {confidence:.2f}"
        else:
            text = None
        # write_text(frame, text)
    
    if bbox is not None:
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), color, 2)


    frame_show = cv2.resize(frame, (480, 640))

    if text is not None:
        write_text(frame_show, text)
    else:
        write_text(frame_show, "")

    write_header(frame_show)

    # Write frame to output video
    out.write(frame_show)

    

    # Display the frame
    cv2.imshow('Frame', frame_show)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and writer objects
cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Output video saved as {output_path}")
