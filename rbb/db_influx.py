# Save data to influx db

import influxdb
import threading
import queue
import sys
import logging as log

from rbb import configuration


class DbInflux:
    def __init__(self):
        self.host = "localhost"
        self.queue = None

        settings = configuration.influxdb_setttings
        self.db_name =  settings.get("DB_NAME", None)
        log.debug(f'InfluxDB "DB_NAME" = {self.db_name}')

        if not self.db_name:
            log.info('InfluxDB not configured. "DB_NAME" not set')
            return

        if "HOST" in settings:
            self.host = settings["HOST"]

        log.info(f"InfluxDB HOST {self.host}, DB  {self.db_name}")

        self.client = influxdb.InfluxDBClient(host=self.host, port=8086)
        self.client.switch_database(self.db_name)

        self.queue = queue.Queue()
        # Todo: config as input
        self.queue = queue.Queue()
        threading.Thread(target=self._queue_reader, daemon=True).start()

    def insert_data(self, mac, name, char_name, signed_int):
        if not self.queue:
            log.debug("InfluxDB not configured")
            return

        item = {}
        item["MAC"] = mac
        item["NAME"] = name
        item["CHARACTERISTIC"] = char_name
        item["DATA"] = signed_int

        self.queue.put(item)

    def _queue_reader(self):
        while True:
            try:
                item = self.queue.get()
                self._insert_data(item["MAC"], item["NAME"], item["CHARACTERISTIC"], item["DATA"])
            except:
                e = sys.exc_info()[0]
                log.error(f"_queue_reader exception: {e}")

    def _insert_data(self, mac, name, char_name, signed_int):
        log.info("Write to db")
        json_body = [
            {
                "measurement": "RaspberryBlueBridge",
                "tags": {
                    "mac": mac,
                    "name": name,
                    "characteristic": char_name,
                },
                "fields": {
                    "value": signed_int
                }
            }
        ]
        if not self.client:
            log.error("_insert_data: NO CLIENT")
            return

        res = self.client.write_points(json_body)
        log.info(f"Wrote to db, result: {res}")
