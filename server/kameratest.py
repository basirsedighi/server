# CVBpy Example Script
#
# 1. Open the GenICam.vin driver.
# 2. Acquire images.
#
# Requires: -

import os
import cvb
from core.camera import Camera
import cv2
import numpy as np

camera = Camera(0)
#camera2 = Camera(1)

camera.start_stream()

while True:
    image, status = camera.get_image()
    if status == cvb.WaitStatus.Ok:

        np_image = cvb.as_array(image, copy=False)

    # Window name in which image is displayed
        window_name = 'image'
        image.save("test.png")
    # Using cv2.imshow() method
    # Displaying the image
        cv2.imshow(window_name, np_image)

    # waits for user to press any key
    # (this is necessary to avoid Python kernel form crashing)
        if cv2.waitKey(1) == 27:
            break

    # closing all open windows
cv2.destroyAllWindows()
