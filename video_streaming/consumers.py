from channels.generic.websocket import WebsocketConsumer, SyncConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import redis
import threading
import datetime


class QRCodeStreamConsumer(WebsocketConsumer):
    send_data = False
    channel_layer = get_channel_layer();

    def connect(self):

        self.accept()

        self.channel_layer = get_channel_layer()

        async_to_sync(self.channel_layer.send)(
            'start-code-reading',
            {
                'type': 'readCodes'
            },
        )

        # redis objects init
        self.redis_obj = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
        self.pubsub = self.redis_obj.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('qr-text-data')

        self.codes = []

        self._log_event = threading.Event()
        self._log_event.set()
        log_thread = threading.Thread(target=self._log_update)
        log_thread.start()

    def disconnect(self, close_code):

        async_to_sync(self.channel_layer.send)(
            'start-code-reading',
            {
                'type': 'stopProcessing'
            },
        )

        self._log_event.clear()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


    def _log_update(self):
        while self._log_event.is_set():
            message = self.pubsub.get_message()

            if message is not None:
                if message['data'] not in self.codes:
                    self.codes.append(message['data'])
                    qrData = str(datetime.datetime.now()) + ' ' + message['data']
                    self.send(json.dumps({
                        'message': qrData
                    }))
        print('exiting logging')
        return









