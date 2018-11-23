from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse, HttpResponseServerError
import cv2
from django.views.decorators import gzip
import time
import redis
import numpy as np


def home(request):
    return render(request, 'video_streaming/home.html')


def about(request):
    return render(request, 'video_streaming/about.html')


class VideoCamera(object):
    def __init__(self):
        # redis objects init
        self.redis_obj = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis_obj.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('img-stream')

    def __del__(self):
        pass

    def get_frame(self):
        message = self.pubsub.get_message()

        if message is None:
            return -1

        nparr = np.fromstring(message['data'], np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        ret, img = cv2.imencode('.jpg', img)
        return img.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()


        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def stream_from_redis(camera):
    while True:
        img = camera.get_frame()
        if img is -1:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')

        time.sleep(0.01)


@gzip.gzip_page
def index(request):
    try:
        return StreamingHttpResponse(stream_from_redis(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")


def html_stream(request):
    return render(request, 'video_streaming/stream.html')
