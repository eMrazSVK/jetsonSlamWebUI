from time import sleep
from channels.consumer import SyncConsumer


class MavlinkDataConsumer(SyncConsumer):
    def fetchStart(self, message):
        while True:
            print('dzjeah idu workers')
            sleep(2)

