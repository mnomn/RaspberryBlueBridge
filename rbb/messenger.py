import sys
import threading
import queue
import paho.mqtt.publish as publish
import logging as log

from rbb import configuration


class Messenger:
    def __init__(self):
        self.host = "localhost"
        self.port = 1883
        self.auth = None

        settings = configuration.mqtt_setttings
        if "HOST" in settings:
            self.host = settings["HOST"]
        if "PORT" in settings:
            self.port = settings["PORT"]
        if ("USERNAME" in settings) and ("PASSWORD" in settings):
            self.auth = {}
            self.auth["username"] = settings["USERNAME"]
            self.auth["password"] = settings["PASSWORD"]

        log.info(f"MQTT HOST {self.host}, PORT  {self.port}")

        self.queue = queue.Queue()
        # Todo: config as input
        self.queue = queue.Queue()
        threading.Thread(target=self.mqttPost, daemon=True).start()

    def sendMessage(self, mac, name, char_guid, data):
        item = {}
        item["TOPIC"] = f"{mac}/{name}/{char_guid}"
        item["DATA"] = data

        self.queue.put(item)

    def mqttPost(self):
        while True:
            try:
                item = self.queue.get()
                log.debug(f"Send MQTT message: {item} to {self.host}")
                publish.single(
                    item["TOPIC"], item["DATA"], auth=self.auth,
                    hostname=self.host, port=int(self.port)
                )
            except:
                e = sys.exc_info()[0]
                log.error(f"mqttPost exception: {e}")