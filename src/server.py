from abc import abstractmethod, ABC
from functools import lru_cache
import logging
from typing import Any, Optional, TypedDict

from .helpers import slugify, with_retries
from .enums import DataType, HAEntityType, RegisterTypes, Parameter, DeviceClass, WriteParameter, WriteSelectParameter, device_class_to_rounding
from .client import Client, ModbusException
from .options import ServerOptions

logger = logging.getLogger(__name__)

class Server(ABC):
    """
    Base server class. Represents modbus server: its name, serial, model, modbus slave_id. e.g. SungrowInverter(Server).

        Includes functions to be abstracted by model/ manufacturer-specific implementations for
        decoding, encoding data read/ write, reading model code, setting up model-specific registers and checking availability.
    """

    def __init__(self, name, serial, modbus_id, connected_client) -> None:
        self.name: str = name
        self.serial: str = serial
        self.modbus_id: int = modbus_id
        self.connected_client: Client = connected_client

        self._model: str = "unknown"

        self.holding_state: list[int] = []      # registers read over self.holding_extent   (min, max)
        self.input_state: list[int] = []        # registers read over self.input_extent     (min, max)

        logger.info(f"Server {self.name} set up.")

    def __str__(self):
        return f"{self.name}"

    @property
    @abstractmethod
    def supported_models(self) -> tuple[str, ...]:
        """ Return a tuple of string names of all supported models for the implementation."""

    @property
    @abstractmethod
    def manufacturer(self) -> str:
        """ Return a string manufacturer name for the implementation."""

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Parameter]:
        """ Return a dictionary of parameter names and parameter objects."""

    @property
    @abstractmethod
    def write_parameters(self) -> dict[str, WriteParameter | WriteSelectParameter]:
        """ Return a dictionary of WriteParameter names and WriteParameter objects."""

    @property
    @lru_cache
    def all_parameters(self) -> dict[str, Parameter | WriteParameter | WriteSelectParameter]:
        params: dict[str, Parameter | WriteParameter | WriteSelectParameter] =  self.parameters.copy()
        params.update(self.write_parameters)
        return params

    @property
    def write_parameters_slug_to_name(self) -> dict[str, str]:
        """ Return a dictionary of mapping slugs to writeparameter names."""
        write_parameters_slug_to_name: dict[str, str] = {slugify(name):name for name in self.write_parameters.copy()}
        return write_parameters_slug_to_name

    @abstractmethod
    def read_model(self) -> str:
        """
            Reads model name register if available and decodes it.

            :returns: model_name
        """

    @abstractmethod
    def setup_valid_registers_for_model(self):
        """ Server-specific logic for removing unsupported or selecting supported
            registers for the specific model must be implemented.
            Removes invalid registers for the specific model of inverter.
            Requires self.model. Call self.read_model() first."""

    def find_register_extent(self) -> None:
        """ Find the minimum and maximum address of registers to be read for 
            holding and input register types, for read and write parameters.

            init internal state for each:
                self.holding[min_addr,max_addr] np
                self.input[min_addr, max_addr] np

                self.holding_start_offset int min
                self.input_start_offset int min
        """
        logger.info(f"Finding register extents for reading batches")
        parameters: dict[str, Parameter | WriteParameter | WriteSelectParameter] = self.all_parameters

        # sort params into holding and input
        holding_params = [(k, v) for k, v in parameters.items() if v["register_type"] == RegisterTypes.HOLDING_REGISTER]
        input_params = [(k, v) for k, v in parameters.items() if v["register_type"] == RegisterTypes.INPUT_REGISTER]

        # sort by address ascending
        holding_params = sorted(holding_params, key=lambda x: x[1]["addr"])
        input_params = sorted(input_params, key=lambda x: x[1]["addr"])

        # list addresses
        holding_addrs = [i[1]["addr"] for i in holding_params]
        input_addrs = [i[1]["addr"] for i in input_params]


        # account for last item count: meaning the largest address needs to be incremented
        if holding_params and holding_params[-1][1]["count"] != 1:
            holding_addrs.append(holding_params[-1][1]["count"] - 1 + holding_params[-1][1]["addr"])
        if input_params and input_params[-1][1]["count"] != 1:
            input_addrs.append(input_params[-1][1]["count"] - 1 + input_params[-1][1]["addr"])

        logger.info(f"{holding_addrs=}")
        logger.info(f"{input_addrs=}")

        # save min (offset) for internal state
        self.holding_addr_extent = (min(holding_addrs), max(holding_addrs))     # TODO assumes there are both holding and input registers defined. maybe ensure this assumption holds as it is a valid one
        self.input_addr_extent = (min(input_addrs), max(input_addrs))
        logger.info(f"{self.holding_addr_extent=}")
        logger.info(f"{self.input_addr_extent=}")


    def create_batches(self, batch_size=125):
        """
        stores (uneven) batches for input and holding register addresses (self.holding_addr_extent, self.input_addr_extent)
                self.holding_batches
                self.input_batches
        """
        def batch(iterable, batch_size=1):
            l = len(iterable)
            for ndx in range(0, l, batch_size):
                yield iterable[ndx:min(ndx + batch_size, l)]

        self.holding_batches = tuple(batch(range(self.holding_addr_extent[0], self.holding_addr_extent[1]+1), batch_size))
        self.input_batches = tuple(batch(range(self.input_addr_extent[0], self.input_addr_extent[1]+1), batch_size))

        logger.debug("")
        logger.info(f"Created batches for server {self.name}")
        logger.debug(f"{self.holding_batches=}")
        logger.debug(f"{self.input_batches}")
        logger.debug("")

    @staticmethod
    @abstractmethod
    def _decoded(registers: list, dtype: DataType):
        """
        Server-specific decoding for registers read.

        Parameters:
        -----------
        registers: list: list of ints as read from 16-bit ModBus Registers
        dtype: (DataType.U16, DataType.I16, DataType.U32, DataType.I32, ...)
        """

    @staticmethod
    @abstractmethod
    def _encoded(value: int, dtype: DataType) -> list[int]:
        "Server-specific encoding of content"

    @property
    def model(self) -> str:
        """ Return a string model name for the implementation.
            Ahould be read in using server.read_model(). 
            server.set_model is called in server.connect(), which sets the model.
            
            model is used in seupt_valid_registers_for_model
            Provided to fascilitate server types where the model cannot be read."""
        return self._model
    
    @model.setter
    def model(self, value):
        self._model = value

    def set_model(self):
        """
            Reads model-holding register, decodes it and sets self.model: str to its value..
            Specify decoding in Server.device_info = {modelcode:    {name:modelname, ...}  }
        """
        logger.info(f"Reading model for server {self.name}")
        self.model = self.read_model()
        logger.info(f"Model read as {self.model}")

        if self.model not in self.supported_models:
            raise ValueError(
                f"Model not supported in implementation of Server, {self}")

    def is_available(self, register_name="Device type code"):
        """ Contacts any server register and returns true if the server is available """
        logger.info(f"Verifying availability of server {self.name}")

        available = True

        address = self.parameters[register_name]["addr"]
        dtype = self.parameters[register_name]["dtype"]
        count = self.parameters[register_name]['count']
        register_type = self.parameters[register_name]['register_type']
        slave_id = self.modbus_id

        try:
            response = self.connected_client.read(
                address, count, slave_id, register_type)
        except ModbusException as e:
            logger.error(f"{e}")
            return False
        except OSError as e:
            logger.error(f"{e}")
            return False

        if response.isError():
            self.connected_client._handle_error_response(response)
            available = False

        return available
    
    def read_batches(self):
        """
        Read holding and input registers for the server in batches of size 125, and save to internal state
        """
        self.holding_state = []
        self.input_state = []

        for batch in self.holding_batches:
            logger.info(f"Reading holding batch from {batch[0]} to {batch[-1]}, {len(batch)=}")
            result = self.connected_client.read(
                batch[0], len(batch), self.modbus_id, RegisterTypes.HOLDING_REGISTER)   # TODO check

            if result.isError():
                self.connected_client._handle_error_response(result)
                raise Exception(f"Error reading batch {batch=}")
            
            self.holding_state.extend(result.registers)
            
        for batch in self.input_batches:
            logger.info(f"Reading input batch from {batch[0]} to {batch[-1]}, {len(batch)=}")
            result = self.connected_client.read(
                batch[0], len(batch), self.modbus_id, RegisterTypes.INPUT_REGISTER)

            if result.isError():
                self.connected_client._handle_error_response(result)
                raise Exception(f"Error reading batch {batch=}")
            
            self.input_state.extend(result.registers)

    def read_from_state(self, parameter_name: str):
        param = self.all_parameters.get(parameter_name)  # type: ignore
        if param is None:
            raise ValueError(f"Attempted to read {parameter_name=} for server {self.name}, but it is not defined")

        address = param["addr"]
        dtype = param["dtype"]
        multiplier = param["multiplier"]
        count = param["count"]
        device_class = param.get("device_class")
        modbus_id = self.modbus_id
        register_type = param["register_type"]

        logger.debug(
            f"Reading param {parameter_name} ({register_type}) of {dtype=} from {address=}, {multiplier=}, {count=}, {self.modbus_id=} from internal state")

        if register_type == RegisterTypes.HOLDING_REGISTER:
            # logger.debug(f"{address=}, {count=}, offset={self.holding_addr_extent[0]}")
            # logger.debug(f"start {address-self.holding_addr_extent[0]}, exclusive_end = { address+count-self.holding_addr_extent[0]}")
            result = self.holding_state[address-self.holding_addr_extent[0]: address+count-self.holding_addr_extent[0]] # address is 1-indexed
        elif register_type == RegisterTypes.INPUT_REGISTER:
            result = self.input_state[address-self.input_addr_extent[0]: address+count-self.input_addr_extent[0]] # address is 1-indexed
        else: 
            raise ValueError(f"Illegal register_type {register_type}. for register {parameter_name}")

        logger.debug(f"Raw register begin value: {result[0]}")
        val = self._decoded(result, dtype)
        if multiplier != 1:
            val *= multiplier
        if device_class is not None and isinstance(val, int) or isinstance(val, float):
            val = round(
                val, device_class_to_rounding.get(device_class, 2)) # type: ignore
        # logger.debug(f"Decoded Value = {val} {unit}")

        return val

    def read_registers(self, parameter_name: str):
        """ 
        Read a group of registers (parameter) using pymodbus

            Requires implementation of the abstract method 'Server._decoded()'

            Parameters:
            -----------
                - parameter_name: str: slave parameter name string as defined in register map
        """
        param = self.parameters.get(parameter_name, self.write_parameters.get(parameter_name))  # type: ignore
        if param is None:
            logger.info(f"No parameter {parameter_name=} for server {self.name} defined. Attempt to read.")
            raise ValueError(f"No parameter {parameter_name=} for server {self.name} defined. Attempt to read.")

        address = param["addr"]
        dtype = param["dtype"]
        multiplier = param["multiplier"]
        count = param["count"]
        unit = param.get("unit")
        device_class = param.get("device_class")
        modbus_id = self.modbus_id
        register_type = param["register_type"]

        logger.debug(
            f"Reading param {parameter_name} ({register_type}) of {dtype=} from {address=}, {multiplier=}, {count=}, {self.modbus_id=}")

        result = self.connected_client.read(
            address, count, modbus_id, register_type)

        if result.isError():
            self.connected_client._handle_error_response(result)
            raise Exception(f"Error reading register {parameter_name}")

        logger.debug(f"Raw register begin value: {result.registers[0]}")
        val = self._decoded(result.registers, dtype)
        if multiplier != 1:
            val *= multiplier
        if device_class is not None and isinstance(val, int) or isinstance(val, float):
            if unit and unit.startswith('k'): # starts with kilo
                val = round(val, 1) # temp. add more precision to fields in kilo- watt/var/va
            else:
                val = round(
                    val, device_class_to_rounding.get(device_class, 2))
        logger.debug(f"Decoded Value = {val} {unit}")

        return val
    
    def write_registers(self, parameter_name_slug: str, value: Any, modbus_id_override: Optional[int]=None) -> None:
        """ 
        Write a group of registers (parameter) using pymodbus

        Requires implementation of the abstract method 'Server._encoded()'

        Finds correct write register name using mapping from Server.write_registers_slug_to_name
        """
        parameter_name = self.write_parameters_slug_to_name[parameter_name_slug]
        param = self.write_parameters[parameter_name]

        address = param["addr"]
        dtype = param["dtype"]
        multiplier = param["multiplier"]
        count = param["count"]  # TODO
        if modbus_id_override is not None: 
            modbus_id = modbus_id_override
        else:
            modbus_id = self.modbus_id
        register_type = param["register_type"]
        unit = param.get("unit")

        if param["ha_entity_type"] == HAEntityType.SWITCH:
            value = int(value, base=0) # interpret string as integer literal. supports auto detecting base
        elif dtype != DataType.UTF8:
            value = float(value)
            if multiplier != 1:
                value /= multiplier
        print(value, dtype)
        values = self._encoded(value, dtype)

        logger.info(
            f"Writing {values} to param {parameter_name} ({register_type}) of {dtype=} from {address=}, {multiplier=}, {count=}, {modbus_id=}")

        # attempt to write to the register 3 times
        try:
            with_retries(self.connected_client.write,
                        values, address, modbus_id, register_type,
                        exception = ModbusException,
                        msg = f"Error writing register {parameter_name}")
        except ModbusException as e:
            logger.error(f"Failure to write after 3 attempts. Continuing")
            return

        if param.get("unit") is not None:
            logger.info(f"Wrote {value=} unit={param.get('unit')} as {values=} to {parameter_name}.")
        else:
            logger.info(f"Wrote {value=} as {values=} to {parameter_name}.")

    def connect(self):
        logger.debug(f"Connecting to server {self}")
        try:
            self.connected_client.connect()
        except ConnectionError:
            logger.error(f"Could not connect to the modbus client while attempting server connection")
            raise

        if not self.is_available():
            logger.error(f"Server {self.name} not available")
            raise ConnectionError()
        self.set_model()
        self.setup_valid_registers_for_model()
        self.find_register_extent()
        self.create_batches()

    @classmethod
    def from_ServerOptions(
        cls,
        opts: ServerOptions,
        clients: list[Client]
    ):
        """
        Initialises modbus_mqtt.server.Server from modbus_mqtt.loader.ServerOptions object

        Parameters:
        -----------
            - sr_options: modbus_mqtt.loader.ServerOptions - options as read from config json
            - clients: list[modbus_mqtt.client.Client] - list of all TCP/Serial clients connected to machine
        """
        name = opts.name
        serial = opts.serialnum
        modbus_id: int = opts.modbus_id  # modbus slave_id

        try:
            clients_names = [str(client) for client in clients]
            logger.info(f"{clients_names}")
            idx = clients_names.index(opts.connected_client)  # TODO ugly
        except ValueError:
            raise ValueError(
                f"Client {opts.connected_client} from server {name} config not defined in client list: {clients_names}"
            )
        connected_client = clients[idx]

        return cls(name, serial, modbus_id, connected_client)
