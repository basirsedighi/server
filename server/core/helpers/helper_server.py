import cvb
import cv2
import base64


def cvbImage_b64():
    """Return a b64 string

    parameter: cvb Image
    """

    image_np = cvb.as_array(frame, copy=True)
    image_rot = cv2.cv2.ROTATE_90_CLOCKWISE
    _, frame = cv2.imencode('.jpg', image_rot)
    im_bytes = frame.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    base64_string = im_b64.decode('utf-8')

    return base64_string
