from PIL import Image
import piexif
import io
import os
from os import path

#im = Image.open("C:/Users/tor_9/Documents/test_jpg/image.jpg")
#exif_dict = piexif.load("C:/Users/tor_9/Documents/test_jpg/image.jpg")
GPScoordinates = u"1989:88:66 55:99:99"  



o = io.BytesIO()
thumb_im = Image.open("C:/Users/tor_9/Documents/test_jpg/image.jpg")
thumb_im.thumbnail((50, 50), Image.ANTIALIAS)
thumb_im.save(o, "jpeg")
thumbnail = o.getvalue()


exif_ifd = {piexif.ExifIFD.DateTimeOriginal: u"2099:09:29 10:10:10",
            piexif.ExifIFD.LensMake: u"LensMake",
            piexif.ExifIFD.Sharpness: 65535,
            piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
            }
gps_ifd = {piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
           piexif.GPSIFD.GPSAltitudeRef: 1,
           piexif.GPSIFD.GPSDateStamp: GPScoordinates,
           }  


exif_dict = {"Exif":exif_ifd, "GPS":gps_ifd, "thumbnail":thumbnail}
exif_bytes = piexif.dump(exif_dict)
piexif.insert(exif_bytes, "C:/Users/tor_9/Documents/test_jpg/image.jpg")


