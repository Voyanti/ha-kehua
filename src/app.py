from abc import ABC, abstractmethod
import os
import signal
from time import sleep
from datetime import datetime, timedelta
import atexit
import logging
from queue import Queue
from typing import final

from .loader import load_validate_options
from .options import AppOptions
from .client import Client
from .implemented_servers import ServerTypes
from .server import Server
from .modbus_mqtt import MqttClient
from paho.mqtt.enums import MQTTErrorCode
from paho.mqtt.client import MQTTMessage

import sys

logging.basicConfig(
    level=logging.INFO,  # Set logging level
    # Format with timestamp
    format="%(asctime)s - %(levelname)s - [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
)
logger = logging.getLogger(__name__)

READ_INTERVAL = 0.001


def exit_handler(
    servers: list[Server], modbus_clients: list[Client], mqtt_client: MqttClient
) -> None:
    logger.info("Exiting")
    # publish offline availability for each server
    for server in servers:
        mqtt_client.publish_availability(False, server)
    logger.info("Closing client connections on exit")
    for client in modbus_clients:
        client.close()

    # messages.wait_for_publish()
    mqtt_client.loop_stop() # doesn't guarentee that all messages are published

class MessageHandler:
    def __init__(self, servers: list[Server], mqtt_client: MqttClient):
        self.devices = servers
        self.mqtt_client = mqtt_client

    def _decode_subscribed_topic(self, msg_topic: str) -> tuple[Server, str]:
        """
            Finds the implicated device and its register, by MQTT message topic.

        Args:
            msg_topic (str): topic of the incoming message (usually a command_topic)

        Raises:
            ValueError: If the command_topic format does not match any of the defined devices

        Returns:
            tuple[str, str]: _description_
        """
        # command_topic = f"{self.base_topic}/{server.nickname}/{slugify(register_name)}/set"
        server_ha_display_name: str = msg_topic.split('/')[1]
        s = None
        for s in self.devices: 
            if s.name == server_ha_display_name:
                device = s
        if s is None: raise ValueError(f"Server {server_ha_display_name} not available. Cannot write.")
        register_name: str = msg_topic.split('/')[2]

        return (device, register_name)

    def decode_and_write(self, msg_topic: str, msg_payload_decoded: str) -> None:
        """
            Finds implied register from topic, writes and updates entity state by a read back.
        """
        # find implied register from topic
        server, register_name = self._decode_subscribed_topic(msg_topic)

        # write
        server.write_registers(register_name, msg_payload_decoded)

        # update state by read back
        value = server.read_registers(server.write_parameters_slug_to_name[register_name])
        logger.info(f"Read back after write attempt {value=}")
        self.mqtt_client.publish_to_ha(
            register_name, value, server)
    
class IDeviceInstantiatorCallbacks(ABC):
    @staticmethod
    @abstractmethod
    def instantiate_clients(OPTIONS: AppOptions) -> list[Client]:
        """ Callback function that creates a list of Client objects from OPTIONS.clients

        Args:
            OPTIONS (AppOptions): AppOptions dataclass containing client configuration

        Returns:
            list[Client]: list of Clients or spoofed Clients
        """  

    @staticmethod
    @abstractmethod
    def instantiate_servers(OPTIONS: AppOptions, clients: list[Client]) -> list[Server]:
        """ Callback function that creates a list of Server objects from OPTIONS.servers

        Args:
            OPTIONS (AppOptions): AppOptions dataclass containing servers configuration
            clients (list[Client]): list of Clients or spoofed Clients

        Returns:
            list[Server]: list of Servers
        """
        
class RealDeviceInstantiator(IDeviceInstantiatorCallbacks):
    @staticmethod
    def instantiate_clients(OPTIONS: AppOptions) -> list[Client]:
        return [Client(cl_options) for cl_options in OPTIONS.clients]

    @staticmethod
    def instantiate_servers(OPTIONS: AppOptions, clients: list[Client]) -> list[Server]:
        return [
            ServerTypes[sr.server_type].value.from_ServerOptions(sr, clients)
            for sr in OPTIONS.servers
        ]
    


class App:
    def __init__(self, device_instantiator: IDeviceInstantiatorCallbacks, message_handler_instantiator: type[MessageHandler], options_rel_path=None) -> None:
        # Read configuration
        self.OPTIONS: AppOptions = load_validate_options(options_rel_path if options_rel_path else "/data/options.json")

        # Setup callbacks
        self.device_instantiator = device_instantiator
        self.message_handler_instantiator = message_handler_instantiator
        

    def setup(self) -> None:
        self.sleep_if_midnight()

        logger.info("Instantiate clients")
        self.clients = self.device_instantiator.instantiate_clients(self.OPTIONS)
        logger.info(f"{len(self.clients)} clients set up")

        logger.info("Instantiate servers")
        self.servers = self.device_instantiator.instantiate_servers(
            self.OPTIONS, self.clients)
        logger.info(f"{len(self.servers)} servers set up")


    def connect(self) -> None:
        for client in self.clients:
            client.connect()

        for server in self.servers:
            server.connect()

        # Setup MQTT Client
        logger.info(f"Connecting to MQTT broker")
        self.mqtt_client = MqttClient(self.OPTIONS)
        self.mqtt_client.connect_timeout = 20

        for i in range(2):
            try: 
                succeed: MQTTErrorCode = self.mqtt_client.connect(
                    host=self.OPTIONS.mqtt_host, port=self.OPTIONS.mqtt_port
                )
                if succeed.value != 0:
                    logger.info(
                        f"MQTT Connection error: {succeed.name}, code {succeed.value}")
                    
            # except ConnectionRefusedError as con_err:
            #     logger.error(f"Connection refused. Sleep 1 min and retry")
            #     sleep(60)
            except Exception as e:
                logger.error(f"{e} \n\n Sleep 1 min and retry mqtt connection")
                sleep(60)

        
        self.message_handler = self.message_handler_instantiator(self.servers, self.mqtt_client)
        self.mqtt_client.message_handler = self.message_handler.decode_and_write

        atexit.register(exit_handler, self.servers,
                        self.clients, self.mqtt_client)

        sleep(READ_INTERVAL)
        self.mqtt_client.loop_start()
        sleep(READ_INTERVAL)

        self.mqtt_client.ensure_connected(self.OPTIONS.mqtt_reconnect_attempts)

        # Publish Discovery Topics
        for server in self.servers:
            self.mqtt_client.publish_discovery_topics(server)

    def loop(self, loop_once=False) -> None:
        if not self.servers or not self.clients:
            logger.info(f"In loop but app servers or clients not setup up")
            raise ValueError(
                f"In loop but app servers or clients not setup up")

        # every read_interval seconds, read the registers and publish to mqtt
        while True:
            self.mqtt_client.ensure_connected(self.OPTIONS.mqtt_reconnect_attempts)

            for server in self.servers:
                for write_register_name, _ in server.write_parameters.items():
                    sleep(READ_INTERVAL)
                    value = server.read_registers(write_register_name)
                    self.mqtt_client.publish_to_ha(
                        write_register_name, value, server)
                logger.info(
                    f"Published all Write parameter values for {server.name=}")
                for register_name, details in server.parameters.items():
                    sleep(READ_INTERVAL)
                    value = server.read_registers(register_name)
                    self.mqtt_client.publish_to_ha(
                        register_name, value, server)
                logger.info(
                    f"Published all Read parameter values for {server.name=}")
            if loop_once:   # for debug/ testing
                break

            logger.info(f"Blocking for {self.OPTIONS.pause_interval_seconds}s")
            sleep(self.OPTIONS.pause_interval_seconds)

            self.sleep_if_midnight()

    def sleep_if_midnight(self) -> None:
        """
        Sleeps if the current time is within 3 minutes before or 5 minutes after midnight.
        Uses efficient sleep intervals instead of busy waiting.
        """
        while self.OPTIONS.midnight_sleep_enabled:
            current_time = datetime.now()
            is_before_midnight = current_time.hour == 23 and current_time.minute >= 57
            is_after_midnight = current_time.hour == 0 and current_time.minute < self.OPTIONS.midnight_sleep_wakeup_after

            if not (is_before_midnight or is_after_midnight):
                break

            # Calculate appropriate sleep duration
            if is_before_midnight:
                # Calculate time until midnight
                next_check = (current_time + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            else:
                # Calculate time until 5 minutes after midnight
                next_check = current_time.replace(
                    hour=0, minute=self.OPTIONS.midnight_sleep_wakeup_after, second=0, microsecond=0)

            # Sleep until next check, but no longer than 30 seconds at a time
            sleep_duration = min(
                30, (next_check - current_time).total_seconds())
            sleep(sleep_duration)





if __name__ == "__main__":
    if len(sys.argv) <= 1:  # deployed on homeassistant
        device_instantiator = RealDeviceInstantiator()
        app = App(device_instantiator=device_instantiator, 
                  message_handler_instantiator=MessageHandler)
        app.setup()
        app.connect()
        app.loop()
    else:                   # running locally
        from .client import SpoofClient

        @final
        class SpoofDeviceInstantiator(RealDeviceInstantiator):
            @staticmethod
            def instantiate_clients(OPTIONS) -> list[SpoofClient]:
                    return [SpoofClient()]

        device_instantiator = SpoofDeviceInstantiator()
        app = App(device_instantiator, MessageHandler, sys.argv[1])
        app.OPTIONS.mqtt_host = "localhost"
        app.OPTIONS.mqtt_port = 1884
        app.OPTIONS.pause_interval_seconds = 10

        app.setup()
        for s in app.servers:
            s.connect = lambda: None
        app.connect()
        app.loop(False)

    # finally:
    #     exit_handler(servers, clients, mqtt_client) TODO NB
