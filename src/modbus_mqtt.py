import os
import signal
from typing import Callable
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
import logging

from .helpers import slugify
from .options import AppOptions

from random import getrandbits
from time import time, sleep
from queue import Queue

from .enums import HAEntityType

logger = logging.getLogger(__name__)
# RECV_Q: Queue = Queue()



class MqttClient(mqtt.Client):
    """
        paho MQTT abstraction for home assistant
    """
    def __init__(self, options: AppOptions) -> None:
        def generate_uuid():
            random_part = getrandbits(64)
            # Get current timestamp in milliseconds
            timestamp = int(time() * 1000)
            node = getrandbits(48)  # Simulating a network node (MAC address)

            uuid_str = f'{timestamp:08x}-{random_part >> 32:04x}-{random_part & 0xFFFF:04x}-{node >> 24:04x}-{node & 0xFFFFFF:06x}'
            return uuid_str

        uuid = generate_uuid()
        super().__init__(CallbackAPIVersion.VERSION2, f"modbus-{uuid}")
        self.username_pw_set(options.mqtt_user, options.mqtt_password)
        self.base_topic = options.mqtt_base_topic
        self.ha_discovery_topic = options.mqtt_ha_discovery_topic

        def on_connect(client, userdata, connect_flags, reason_code, properties):
            if reason_code == 0:
                logger.info(f"Connected to MQTT broker.")
            else:
                logger.info(
                    f"Not connected to MQTT broker.\nReturn code: {reason_code=}")

        def on_disconnect(client,
                        userdata,
                        disconnect_flags,
                        reason,
                        properties):
            logger.error(f"Disconnected from MQTT broker, {reason=}\n{disconnect_flags=}\n{properties=}")
            logger.info(f"Stopping all threads")
            os.kill(os.getpid(), signal.SIGINT)

        def on_message(client, userdata, message):
            logger.info("Received message on MQTT")
            try: 
                self.message_handler(msg.topic, msg.payload.decode('utf-8'))

            except Exception as e:
                logger.error(f"Exception while handling received message. Stop Process. \n {e}")
                os.kill(os.getpid(), signal.SIGINT)

        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_message = on_message

        self.message_handler = Callable[[str, str], None]

    def publish_discovery_topics(self, server) -> None:
        # TODO check if more separation from server is necessary/ possible
        nickname = server.name
        if not server.model or not server.manufacturer or not server.serial or not nickname or not server.parameters:
            logging.info(
                f"Server not properly configured. Cannot publish MQTT info")
            raise ValueError(
                f"Server not properly configured. Cannot publish MQTT info")

        logger.info(f"Publishing discovery topics for {nickname}")
        device = {
            "manufacturer": server.manufacturer,
            "model": server.model,
            "identifiers": [f"{nickname}"],
            "name": f"{nickname}"
            # "name": f"{server.manufacturer} {server.serialnum}"
        }

        # publish discovery topics for legal registers
        # assume registers in server.registers
        availability_topic = f"{self.base_topic}_{nickname}/availability"

        parameters = server.parameters

        for register_name, details in parameters.items():
            state_topic = f"{self.base_topic}/{nickname}/{slugify(register_name)}/state"
            discovery_payload = {
                "name": register_name,
                "unique_id": f"{nickname}_{slugify(register_name)}",
                "state_topic": state_topic,
                "availability_topic": availability_topic,
                "device": device,
                # "device_class": details["device_class"].value,
            }
            if details["device_class"] is not None:
                discovery_payload["device_class"] = details["device_class"].value
            if details["unit"] != "":
                discovery_payload.update(unit_of_measurement=details["unit"])
            state_class = details.get("state_class", False)
            if state_class:
                discovery_payload['state_class'] = state_class
                
            if details.get("value_template") is not None:
                discovery_payload.update(value_template=details["value_template"])
                
            discovery_topic = f"{self.ha_discovery_topic}/sensor/{nickname}/{slugify(register_name)}/config"

            self.publish(discovery_topic, json.dumps(
                discovery_payload), retain=True)

        self.publish_availability(True, server)

        for register_name, details in server.write_parameters.items():
            item_topic = f"{self.base_topic}/{nickname}/{slugify(register_name)}"
            discovery_payload = {
                # required
                "command_topic": item_topic + f"/set", 
                "state_topic": item_topic + f"/state",
                # optional
                "name": register_name,
                "unique_id": f"{nickname}_{slugify(register_name)}",
                # "unit_of_measurement": details["unit"],
                "availability_topic": availability_topic,
                "device": device,
            }
            if details.get("unit") is not None:
                discovery_payload.update(unit_of_measurement=details["unit"])
            if details.get("options") is not None:
                discovery_payload.update(options=details["options"])
                if details.get("value_template") is not None:
                    discovery_payload.update(value_template=details["value_template"])
                if details.get("command_template") is not None:
                    discovery_payload.update(command_template=details["command_template"])
            if details.get("min") is not None and details.get("max") is not None:
                discovery_payload.update(min=details["min"], max=details["max"])
            if details.get("payload_off") is not None and details.get("payload_on") is not None:
                discovery_payload.update(payload_off=details["payload_off"], payload_on=details["payload_on"])

            discovery_topic = f"{self.ha_discovery_topic}/{details['ha_entity_type'].value}/{nickname}/{slugify(register_name)}/config"
            self.publish(discovery_topic, json.dumps(discovery_payload), retain=True)

            # subscribe to write topics
            self.subscribe(discovery_payload["command_topic"])

    def publish_to_ha(self, register_name, value, server):
        nickname = server.name
        state_topic = f"{self.base_topic}/{nickname}/{slugify(register_name)}/state"
        msg_info = self.publish(state_topic, value, qos=1)  # , retain=True)
            

    def publish_availability(self, avail, server):
        nickname = server.name
        availability_topic = f"{self.base_topic}_{nickname}/availability"
        msg_info = self.publish(availability_topic,
                     "online" if avail else "offline", qos=1, retain=True)
        

    def ensure_connected(self, max_attempts: int = 3) -> None:
        """Block while not connected to the broker. Retry every second, for _max_attempts_, before stopping the process.
        """ 
        attempt_num = 1

        while not self.is_connected():
            if attempt_num > max_attempts:
                logger.info(f"Not connected to mqtt broker after {max_attempts=}. Kill process")
                os.kill(os.getpid(), signal.SIGINT)

            logger.info(f"Not connected to mqtt broker, sleep 1s and retry. {attempt_num=}")

            sleep(1)
        logger.info(f"Connected to MQTT broker")
