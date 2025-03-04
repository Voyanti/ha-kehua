from typing import final
from .server import Server
import struct
import logging
from .enums import DataType
from .atess_registers import atess_parameters, PBD_parameters, PCS_parameters, not_PCS_parameters

logger = logging.getLogger(__name__)

@final
class AtessInverter(Server):
    # RS485 address is 1-32
    # adresses seem to be 0-indexed so +1
    def __init__(self, name, serial, modbus_id, connected_client):
        super().__init__(name, serial, modbus_id, connected_client)

        self._manufacturer = "Atess"
        self._supported_models = ('PCS150', 'PCS500', 'PBD250') 
        self._serialnum = "unknown"
        self._parameters = atess_parameters
        self._write_parameters = {}
        self._model = "PBD250"
        if modbus_id == 1:
            self._model = "PCS500"

    @property
    def manufacturer(self):
        return self._manufacturer
    
    @property
    def supported_models(self):
        return self._supported_models
    
    @property
    def parameters(self):
        return self._parameters
    
    @property
    def write_parameters(self):
        return self._write_parameters
    
    def is_available(self, register_name="Device On/Off"):
        return super().is_available(register_name)
        
    def read_model(self):
        # model = self.read_registers("Hardware Version")
        logger.info(f"HARDCODED model {self._model=}")

        return self._model
    
    def set_model(self):
        self.model = self.read_model()
        logger.info(f"Model read as {self.model}")
        # no verification TODO temp
    
    def setup_valid_registers_for_model(self):
        logger.info(f"{self.model}")
        if "PCS" in self.model:
            self._parameters.update(PCS_parameters)
            logger.info("Added PCS-Specific Registers.")
        else:
            self._parameters.update(not_PCS_parameters)
            logger.info("Added Registers. common to all except PCS models")

            if "PBD" in self.model:
                self._parameters.update(PBD_parameters)
                logger.info("Added PBD-Specific Registers.")

    def _decoded(cls, registers, dtype):
        def _decode_u16(registers):
            """ Unsigned 16-bit big-endian to int """
            return registers[0]
        
        def _decode_s16(registers):
            """ Signed 16-bit big-endian to int """
            sign = 0xFFFF if registers[0] & 0x1000 else 0
            packed = struct.pack('>HH', sign, registers[0])
            return struct.unpack('>i', packed)[0]
        
        def _decode_utf8(registers):
            """ Two ASCII chars per 16-bit register """
            
            packed = struct.pack('>H', registers[0])
            return packed.decode("utf-8")       

        if dtype == DataType.U16: return _decode_u16(registers)
        elif dtype == DataType.I16: return _decode_s16(registers)
        elif dtype == DataType.UTF8: return _decode_utf8(registers)
        else: raise NotImplementedError(f"Data type {dtype} decoding not implemented")

    def _encoded(cls, value):
        raise NotImplementedError()
   
if __name__ == "__main__":
    inv = AtessInverter("", "", "", "")
    print(inv._decoded([0x6154], DataType.UTF8))# aT = 0x61, 0x54