import sys
import threading
import queue
import paho.mqtt.publish as publish
import logging

from rbb import configuration

log = logging.getLogger("device")

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

        username = settings.get("USERNAME")
        password = settings.get("PASSWORD")
        if username and password:
            self.auth = {}
            self.auth["username"] = username
            self.auth["password"] = password

        log.info(f"HOST {self.host}, PORT  {self.port} USER: {username}")

        self.queue = queue.Queue()
        # Todo: config as input
        self.queue = queue.Queue()
        threading.Thread(target=self.mqttPost, daemon=True).start()

    def sendMessage(self, device_name, char_guid, data):
        item = {}
        item["TOPIC"] = f"{device_name}/{char_guid}"
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