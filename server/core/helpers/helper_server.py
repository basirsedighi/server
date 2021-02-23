import cvb
import cv2
import base64


def cvbImage_b64(frame):
    """Return a b64 string

    parameter: cvb Image
    """

    image_np = cvb.as_array(frame, copy=False)
    # image_rot = cv2.cv2.ROTATE_90_CLOCKWISE
    image_np = cv2.resize(image_np, (640, 480))
    _, frame = cv2.imencode('.jpg', image_np)
    im_bytes = frame.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    base64_string = im_b64.decode('utf-8')

    return base64_string
