import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
import logging

from .helpers import slugify
from .loader import Options

from random import getrandbits
from time import time, sleep
from queue import Queue

logger = logging.getLogger(__name__)
# RECV_Q: Queue = Queue()


class MqttClient(mqtt.Client):
    """
        paho MQTT abstraction for home assistant
    """
    def __init__(self, options: Options) -> None:
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
        self.ha_discovery_topic = options.mwtt_ha_discovery_topic

        def on_connect(client, userdata, connect_flags, reason_code, properties):
            if reason_code == 0:
                logger.info(f"Connected to MQTT broker.")
            else:
                logger.info(
                    f"Not connected to MQTT broker.\nReturn code: {reason_code=}")

        def on_disconnect(client, userdata, message):
            logger.info("Disconnected from MQTT broker")

        def on_message(client, userdata, message):
            logger.info("Received message on MQTT")
            self.message_handler(message)

        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_message = on_message

    def message_handler(self, msg):
        """
            Writes appropriate server registers for each message in mqtt receive queue
        """
        # command_topic = f"{self.base_topic}/{server.nickname}/{slugify(register_name)}/set"
        server_ha_display_name: str = msg.topic.split('/')[1]
        s = None
        for s in self.servers: 
            if s.name == server_ha_display_name:
                server = s
        if s is None: raise ValueError(f"Server {server_ha_display_name} not available. Cannot write.")
        register_name: str = msg.topic.split('/')[2]
        value: str = msg.payload.decode('utf-8')

        server.write_registers(register_name, value)


        value = server.read_registers(server.write_parameters_slug_to_name[register_name])
        logger.info(f"read {value=}")
        self.publish_to_ha(
            register_name, value, server)

    def publish_discovery_topics(self, server) -> None:
        while not self.is_connected():
            logger.info(
                f"Not connected to mqtt broker yet, sleep 100ms and retry. Before publishing discovery topics.")
            sleep(0.1)
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
                "device_class": details["device_class"].value,
                "unit_of_measurement": details["unit"],
            }
            state_class = details.get("state_class", False)
            if state_class:
                discovery_payload['state_class'] = state_class
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
                "unit_of_measurement": details["unit"],
                "availability_topic": availability_topic,
                "device": device
            }

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
        self.publish(state_topic, value)  # , retain=True)

    def publish_availability(self, avail, server):
        nickname = server.name
        availability_topic = f"{self.base_topic}_{nickname}/availability"
        self.publish(availability_topic,
                     "online" if avail else "offline", retain=True)
