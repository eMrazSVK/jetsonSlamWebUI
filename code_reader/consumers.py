from channels.consumer import SyncConsumer
import redis
import time
from imutils.video import VideoStream
import cv2
import numpy as np
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import threading


class CodeReaderConsumer(SyncConsumer):


    # meant for running in thread
    def _readCodes(self):
        # object for handling redis
        redis_obj = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

        # camera init
        vid_stream = cv2.VideoCapture(0)

        # param for encoding frame to be sent via redis
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        while self._read_event.is_set():
            _, frame = vid_stream.read()
            frame = imutils.resize(frame, width=400)

            # find the barcodes in the frame and decode each of the barcodes
            barcodes = pyzbar.decode(frame)

            # loop over the detected barcodes
            for barcode in barcodes:
                # extract the bounding box location of the barcode and draw
                # the bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # the barcode data is a bytes object so if we want to draw it
                # on our output image we need to convert it to a string first
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                # draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)

                redis_obj.publish('qr-text-data', text)
                cv2.putText(frame, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            frame = imutils.resize(frame, width=320)
            _, frame = cv2.imencode('.jpg', frame, encode_param)
            data = np.array(frame)
            stringData = data.tostring()
            redis_obj.publish('img-stream', stringData)
            time.sleep(0.05)

        vid_stream.release()
        return


    def readCodes(self, message):
        self._read_event = threading.Event()
        self._read_event.set()
        read_thread = threading.Thread(target=self._readCodes)
        read_thread.start()


    def stopProcessing(self, message):
        self._read_event.clear()
