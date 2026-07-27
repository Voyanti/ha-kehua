import threading
from typing import Optional
from .enums import RegisterTypes
from .options import ModbusTCPOptions, ModbusRTUOptions
from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from pymodbus.pdu import ExceptionResponse, ModbusPDU
from pymodbus.exceptions import ConnectionException, ModbusIOException, ModbusException
import logging
from .options import ModbusTCPOptions, ModbusRTUOptions
from time import sleep

logger = logging.getLogger(__name__)

# Failures meaning the transport is dead/unusable, as opposed to the device
# answering with a modbus error response. BrokenPipeError/ConnectionResetError
# are OSError subclasses; pymodbus wraps some socket failures in
# ConnectionException/ModbusIOException instead of letting the OSError escape.
CONNECTION_ERRORS = (ConnectionException, ModbusIOException, OSError)


class Client:
    """
    Modbus client representation: name, nickname (ha_display_name), and pymodbus client.

    Wraps around pymodbus.client.ModbusSerialClient | pymodbus.client.ModbusTCPClient to
    fan out dictionary information, and decode/ encode register values when reading/ writing/
    """

    def __init__(self, cl_options: ModbusTCPOptions | ModbusRTUOptions):
        """
        Initialised from modbus_mqtt.loader.ClientOptions object

        Parameters:
        -----------
            - cl_options: modbus_mqtt.loader.ClientOptions - options as read from config json

        TODO move to classmethod, to separate home-assistant dependency out
        """
        self.name = cl_options.name
        self.client: ModbusSerialClient | ModbusTcpClient
        # Serialises requests and close/reconnect across threads (main read
        # loop vs paho-mqtt callback thread). RLock so connect() can be called
        # both externally and from within a locked read()/write().
        self._lock = threading.RLock()

        if isinstance(cl_options, ModbusTCPOptions):
            self.client = ModbusTcpClient(host=cl_options.host, port=cl_options.port)
        elif isinstance(cl_options, ModbusRTUOptions):
            self.client = ModbusSerialClient(
                port=cl_options.port,
                baudrate=cl_options.baudrate,
                bytesize=cl_options.bytesize,
                parity="Y" if cl_options.parity else "N",
                stopbits=cl_options.stopbits,
            )

    def _read_once(self, address, count, slave_id, register_type):
        if register_type == RegisterTypes.HOLDING_REGISTER:
            return self.client.read_holding_registers(
                address=address - 1, count=count, device_id=slave_id
            )
        elif register_type == RegisterTypes.INPUT_REGISTER:
            return self.client.read_input_registers(
                address=address - 1, count=count, device_id=slave_id
            )
        else:
            logger.info(f"unsupported register type {register_type}")
            raise ValueError(f"unsupported register type {register_type}")

    def read(self, address, count, slave_id, register_type):
        """
        Calls the appropriate read function, based on the register type (input / holding).

        On a connection error (stale/dead socket): forces a fresh socket and
        retries the read once (reads are idempotent). If the retry also fails,
        closes the socket and raises ConnectionError so the app-level retry
        loop takes over.
        """
        logger.debug(
            f"Reading param from {address=}, {count=} on {slave_id=}, {register_type=}"
        )

        with self._lock:
            try:
                return self._read_once(address, count, slave_id, register_type)
            except ModbusIOException as e:
                # Timeout/no valid response: the device may just be slow —
                # retry without tearing down the transport (reopening a serial
                # port per timeout would churn RTU links).
                logger.warning(
                    f"IO error reading from {self}: {e}. Retrying once"
                )
                force_new_socket = False
            except (ConnectionException, OSError) as e:
                logger.warning(
                    f"Connection error reading from {self}: {e}. Reconnecting and retrying once"
                )
                force_new_socket = True

            try:
                if force_new_socket:
                    self.connect(num_retries=1, sleep_interval=0, force_new_socket=True)
                return self._read_once(address, count, slave_id, register_type)
            except CONNECTION_ERRORS as e:
                try:
                    self.client.close()
                except Exception:
                    logger.warning(f"Error closing client {self} after failed read")
                raise ConnectionError(
                    f"Read from client {self} failed after retry: {e}"
                ) from e

    def write(self, values: list[int], address: int, slave_id: int, register_type):
        """Writes a list of encoded ints to 16-bit registers,
        starting at the 1-indexed address specified

        Args:
            values (list[int]): list of ints encoding the value
            address (int): modbus register address (1-indexed)
            slave_id (int): modbus slave_id
            register_type (RegisterType): only RegisterTypes.HOLDING_REGISTER. Used for validation

        Raises:
            ValueError: if register_type not RegisterTypes.HOLDING_REGISTER
            ModbusException: if a modbus exception occurs

        Returns:
            ModbusPDU: modbus client response
        """
        if not register_type == RegisterTypes.HOLDING_REGISTER:
            logger.info(f"unsupported write register type {register_type}")
            raise ValueError(f"unsupported register type {register_type}")

        with self._lock:
            try:
                result = self.client.write_registers(
                    address=address - 1, values=values, device_id=slave_id
                )
            except CONNECTION_ERRORS as e:
                # Repair the transport, but do NOT re-issue the write here: a
                # failure surfacing one request late means it may already have
                # been applied. Re-issuing is the server layer's decision
                # (with_retries in Server.write_registers).
                logger.warning(
                    f"Connection error writing to {self}: {e}. Reconnecting"
                )
                # single fast attempt: this runs on the paho callback thread
                # holding the client lock — a long repair here stalls the read
                # loop and can starve the MQTT keepalive
                try:
                    self.connect(num_retries=1, sleep_interval=0, force_new_socket=True)
                except ConnectionError:
                    logger.error(f"Reconnect of {self} after write failure failed")
                raise ModbusException(
                    f"Connection error writing register at {address=} on {slave_id=}"
                ) from e

        if result.isError():
            self._handle_error_response(result)
            raise ModbusException(
                f"Error writing register at address {address=} on {slave_id=}"
            )

        return result

    def connect(self, num_retries=2, sleep_interval=3, force_new_socket: bool = False) -> None:
        logger.info(f"Connecting to client {self}")

        with self._lock:
            connected = False
            for i in range(num_retries):
                # pymodbus client.connect short-circuits if it already has a socket
                # validity of socket not checked. a subsequent read can still raise BrokenPipeError
                # force a new connection with close() first
                if force_new_socket:
                    self.client.close()

                connected = self.client.connect()
                if connected:
                    break

                logging.info(f"Couldn't connect to {self}. Retrying")
                if i < num_retries - 1:
                    sleep(sleep_interval)

            if not connected:
                logger.error(f"Client Connection Issue after {num_retries} attempts.")
                raise ConnectionError(f"Client {self} Connection Issue")

        logger.info(f"Sucessfully connected to {self}")

    def close(self):
        logger.info(f"Closing connection to {self}")
        with self._lock:
            self.client.close()

    def __str__(self):
        """
        self.nickname is used as a unique id for finding the client to which each server is connected.
        """
        return f"{self.name}"

    def _handle_error_response(self, result):
        if isinstance(result, ExceptionResponse):
            exception_code = result.exception_code

            # Modbus exception codes and their meanings
            exception_messages = {
                1: "Illegal Function",
                2: "Illegal Data Address",
                3: "Illegal Data Value",
                4: "Slave Device Failure",
                5: "Acknowledge",
                6: "Slave Device Busy",
                7: "Negative Acknowledge",
                8: "Memory Parity Error",
                10: "Gateway Path Unavailable",
                11: "Gateway Target Device Failed to Respond",
            }

            error_message = exception_messages.get(exception_code, "Unknown Exception")
            logger.error(f"Modbus Exception Code {exception_code}: {error_message}")
        else:
            logger.error(f"Non Standard Modbus Exception. Cannot Decode Response")


class SpoofClient:
    """
    Spoofed Modbus client representation: name, nickname (ha_display_name), and pymodbus client.

    Wraps around pymodbus.client.ModbusSerialClient | pymodbus.client.ModbusTCPClient to
    fan out dictionary information, and decode/ encode register values when reading/ writing/
    """

    class SpoofResponse:
        def __init__(self, registers: Optional[list[int]] = None):
            if registers:
                self.registers = registers

        def isError(self):
            return False

    def __init__(self):
        self.name = "client1"

    def read(self, address, count, slave_id, register_type):
        logger.debug(f"SPOOFING READ")
        response = SpoofClient.SpoofResponse([73 for _ in range(count)])
        return response

    def write(self, values: list[int], address: int, slave_id: int, register_type):
        """Writes a list of encoded ints to 16-bit registers,
        starting at the 1-indexed address specified

        Args:
            values (list[int]): list of ints encoding the value
            address (int): modbus register address (1-indexed)
            slave_id (int): modbus slave_id
            register_type (RegisterType): only RegisterTypes.HOLDING_REGISTER. Used for validation

        Raises:
            ValueError: if register_type not RegisterTypes.HOLDING_REGISTER

        Returns:
            ModbusPDU: modbus client response
        """
        if not register_type == RegisterTypes.HOLDING_REGISTER:
            logger.info(f"unsupported write register type {register_type}")
            raise ValueError(f"unsupported register type {register_type}")

        logger.info(
            f"Spoof Write of {values} at {address=} ({register_type=}) of {values=} on {slave_id=}"
        )
        return SpoofClient.SpoofResponse()

    def connect(self, num_retries=2, sleep_interval=3, force_new_socket: bool = False):
        logger.info(f"SPOOFING CONNECT to {self}")

    def close(self):
        logger.info(f"SPOOFING DISCONNECT to {self}")

    def __str__(self):
        """
        self.nickname is used as a unique id for finding the client to which each server is connected.
        """
        return f"{self.name}"
