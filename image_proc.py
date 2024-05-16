import numpy as np
import cv2

# Example: Suppose you have a buffer of uint8 items representing an image
# Let's say the image is 480x640 and each pixel is a uint16 value
width, height = 640, 480
num_pixels = width * height

# Generate a byte buffer for demonstration
# Each pixel is uint16, so we need 2 * num_pixels uint8 items
buffer_uint8 = np.random.randint(0, 256, 2 * num_pixels, dtype=np.uint8)
print(len(buffer_uint8))

# Convert the uint8 buffer to uint16
# The view method will reinterpret the bytes as uint16 values
buffer_uint16 = buffer_uint8.view(dtype=np.uint16)
print(len(buffer_uint16))

# Reshape the uint16 buffer to the image dimensions (height, width)
image_uint16 = buffer_uint16.reshape((height, width))

# If you need to visualize the image or process it further using OpenCV
# For visualization, we may need to normalize or convert to uint8
# Example: Normalize and convert to uint8 for displaying
image_display = cv2.convertScaleAbs(image_uint16, alpha=(255.0/65535.0))

# Display the image using OpenCV
cv2.imshow('Recreated Image', image_display)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Alternatively, save the image if needed
# cv2.imwrite('recreated_image.png', image_display)
