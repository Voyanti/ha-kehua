from typing import Any, Optional, final

from .helpers import slugify
from .server import Server
from pymodbus.client import ModbusSerialClient
import struct
from .enums import DeviceClass, HAEntityType, Parameter, RegisterTypes, DataType, WriteParameter
import logging

logger = logging.getLogger(__name__)

@final
class SungrowLogger(Server):
    # modbus slave id is usually 247
    # Sungrow 1.0.2.7 definitions 04 input registers
    # https://www.studocu.com/row/document/cukurova-universitesi/english-b1-level/ti-20211201-logger-communication-protocol-10/31069893
    logger_input_registers: dict[str, Parameter] = {
        'Device type code': {
            'addr': 8000,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': '',
            'device_class': DeviceClass.ENUM,
            'remarks': '0x0705 Logger3000, 0x0710 Logger1000, 0x0718 Logger4000',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Protocol number': {
            'addr': 8001,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 1,
            'unit': '',
            'device_class': DeviceClass.ENUM,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Communication protocol version': {
            'addr': 8003,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 1,
            'unit': '',
            'device_class': DeviceClass.ENUM,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Total devices connected': {
            'addr': 8005,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'Set',
            'device_class': DeviceClass.ENUM,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Total faulty devices': {
            'addr': 8006,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'Set',
            'device_class': DeviceClass.ENUM,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Digital input state': {
            'addr': 8021,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 1,
            'unit': '',
            'device_class': DeviceClass.ENUM,
            'remarks': 'Currently only the low 16 bits are used. Logger1000 only uses 8 bits, Logger3000 uses 16 bits, and Logger4000 uses 16 bits',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC1 voltage': {
            'addr': 8029,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 0.01,
            'unit': 'V',
            'device_class': DeviceClass.VOLTAGE,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC1 current': {
            'addr': 8030,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 0.01,
            'unit': 'mA',
            'device_class': DeviceClass.CURRENT,
            'remarks': 'Logger1000/Logger3000',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC2 voltage': {
            'addr': 8031,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 0.01,
            'unit': 'V',
            'device_class': DeviceClass.VOLTAGE,
            'remarks': 'Logger1000/Logger3000',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC2 current': {
            'addr': 8032,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 0.01,
            'unit': 'mA',
            'device_class': DeviceClass.CURRENT,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC3 voltage': {
            'addr': 8033,
            'dtype': DataType.I16,
            'count': 1,
            'multiplier': 0.01,
            'unit': 'V',
            'device_class': DeviceClass.VOLTAGE,
            'remarks': 'Logger3000 and Logger1000 share the voltage. Logger3000 consumes 0.01mV, and Logger1000 consumes 0.01V',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC4 voltage': {
            'addr': 8034,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 0.01,
            'unit': 'V',
            'device_class': DeviceClass.VOLTAGE,
            'remarks': 'Logger3000 and Logger1000 share the voltage. Logger3000 consumes 0.01mV, and Logger1000 consumes 0.01V',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC3 current': {
            'addr': 8035,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 0.01,
            'unit': 'mA',
            'device_class': DeviceClass.CURRENT,
            'remarks': 'Logger1000/Logger4000',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'ADC4 current': {
            'addr': 8036,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 0.01,
            'unit': 'mA',
            'device_class': DeviceClass.CURRENT,
            'remarks': 'Logger1000/Logger4000',
            'register_type': RegisterTypes.INPUT_REGISTER},

        'Max. total nominal active power': {
            'addr': 8058,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'kW',
            'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Min. total nominal active power': {
            'addr': 8059,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'kW',
            'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Max. total nominal reactive power': {
            'addr': 8060,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'kVar',
            'device_class': DeviceClass.REACTIVE_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Min. total nominal reactive power': {
            'addr': 8061,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 1,
            'unit': 'kVar',
            'device_class': DeviceClass.REACTIVE_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Inverter preset total active power': {
            'addr': 8066,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'kW',
            'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Inverter preset total reactive power': {
            'addr': 8067,
            'count': 1,
            'dtype': DataType.I16,
            'multiplier': 1,
            'unit': 'kVar',
            'device_class': DeviceClass.REACTIVE_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Logger On/Off state': {
            'addr': 8068,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': '',
            'device_class': DeviceClass.ENUM,
            'remarks': '0: Off, 1: On',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Logger unlatch state': {
            'addr': 8069,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': '',
            'device_class': DeviceClass.ENUM,
            'remarks': '0: latched, 1: unlatched',
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Total active power': {
            'addr': 8070,
            'count': 4,
            'dtype': DataType.I64,
            'multiplier': 1,
            'unit': 'W',
            'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.INPUT_REGISTER,
            'state_class': 'total'},
        'Daily yield': {
            'addr': 8074,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 0.1,
            'unit': 'kWh',
            'device_class': DeviceClass.ENERGY,
            'register_type': RegisterTypes.INPUT_REGISTER,
            'state_class': 'total_increasing'},
        'Total reactive power': {
            'addr': 8076,
            'count': 4,
            'dtype': DataType.I64,
            'multiplier': 1,
            'unit': 'var',
            'device_class': DeviceClass.REACTIVE_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER,
            'state_class': 'total'},
        'Total yield': {
            'addr': 8080,
            'count': 4,
            'dtype': DataType.I64,
            'multiplier': 0.1,
            'unit': 'kWh',
            'device_class': DeviceClass.ENERGY,
            'register_type': RegisterTypes.INPUT_REGISTER,
            'state_class': 'total'},
        'Min. adjustable active power': {
            'addr': 8084,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 0.1,
            'unit': 'kW',
            'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Max. adjustable active power': {
            'addr': 8086,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 0.1,
            'unit': 'kW',
            'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Min. adjustable reactive power': {
            'addr': 8088,
            'count': 2,
            'dtype': DataType.I32,
            'multiplier': 0.1*1000,
            'unit': 'var',
            'device_class': DeviceClass.REACTIVE_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Max. adjustable reactive power': {
            'addr': 8090,
            'count': 2,
            'dtype': DataType.I32,
            'multiplier': 0.1*1000,
            'unit': 'var',
            'device_class': DeviceClass.REACTIVE_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Nominal active power': {
            'addr': 8092,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 0.1*1000,
            'unit': 'W',    # TODO check!
            'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Nominal reactive power': {
            'addr': 8094,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 0.1*1000,
            'unit': 'var',
            'device_class': DeviceClass.REACTIVE_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Grid-connected devices': {
            'addr': 8096,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'Set',
            'device_class': DeviceClass.ENUM,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Off-grid devices': {
            'addr': 8097,
            'count': 1,
            'dtype': DataType.U16,
            'multiplier': 1,
            'unit': 'Set',
            'device_class': DeviceClass.ENUM,
            'register_type': RegisterTypes.INPUT_REGISTER},
        'Monthly yield of array': {
            'addr': 8098,
            'count': 4,
            'dtype': DataType.I64,
            'multiplier': 0.1,
            'unit': 'kWh',
            'device_class': DeviceClass.ENERGY,
            'register_type': RegisterTypes.INPUT_REGISTER,
            'state_class': 'total_increasing'},
        'Annual yield of array': {
            'addr': 8102,
            'count': 4,
            'dtype': DataType.I64,
            'multiplier': 0.1,
            'unit': 'kWh',
            'device_class': DeviceClass.ENERGY,
            'register_type': RegisterTypes.INPUT_REGISTER,
            'state_class': 'total'},
        'Apparent power of array': {
            'addr': 8106,
            'count': 4,
            'dtype': DataType.I64,
            'multiplier': 1,
            'unit': 'VA',
            'device_class': DeviceClass.APPARENT_POWER,
            'register_type': RegisterTypes.INPUT_REGISTER,
            'state_class': 'measurement'}
    }

    # Sungrow Logger holding register 
    # The holding register is set to support single function only. All commands from the
    # broadcast address 0 are directly transparently transmitted to the inverter
    logger_holding_registers: dict[str, WriteParameter] = {
        # 'Set Subarray inverters on or off': {
        #     'addr': 8002,
        #     'count': 1,
        #     'dtype': DataType.U16,
        #     'multiplier': 1,
        #     'unit': '',
        #     # 'device_class': DeviceClass.ENUM,
        #     'register_type': RegisterTypes.HOLDING_REGISTER,
        #     'remarks': '0: Off\n1: On'
        # },
        'Set Subarray inverter active power': {
            'addr': 8003,
            'count': 2,
            'dtype': DataType.U32,
            'multiplier': 0.1,
            'unit': 'kW',
            'min': 0,
            'max': 125,
            'ha_entity_type': HAEntityType.NUMBER,
            # 'device_class': DeviceClass.POWER,
            'register_type': RegisterTypes.HOLDING_REGISTER
        },

        # 'Set active power ratio of subarray inverter': {
        #     'addr': 8005,
        #     'count': 2,
        #     'dtype': DataType.U32,
        #     'multiplier': 0.1,
        #     'unit': '%',
        #     'device_class': 'power_factor',
        #     'register_type': RegisterTypes.HOLDING_REGISTER
        # },

        # 'Set Subarray inverter reactive power': {
        #     'addr': 8007,
        #     'count': 2,
        #     'dtype': DataType.I32,
        #     'multiplier': 0.1,
        #     'unit': 'kVar',
        #     'device_class': DeviceClass.REACTIVE_POWER,
        #     'register_type': RegisterTypes.HOLDING_REGISTER
        # },
        # 'Setting reactive power ratio of subarray inverter': {
        #     'addr': 8009,
        #     'count': 2,
        #     'dtype': DataType.I32,
        #     'multiplier': 0.1,
        #     'unit': '%',
        #     'device_class': 'power_factor',
        #     'register_type': RegisterTypes.HOLDING_REGISTER
        # },
        # 'Set the power factor of subarray inverter': {
        #     'addr': 8011,
        #     'count': 2,
        #     'dtype': DataType.I32,
        #     'multiplier': 0.001,
        #     'unit': '',
        #     'device_class': 'power_factor',
        #     'register_type': RegisterTypes.HOLDING_REGISTER
        # },
    }

    # write_parameters = {}


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # self.model = "Logger 1000x"              # only 1000b model
        self._manufacturer = "Sungrow"
        self._parameters = self.logger_input_registers
        self.serial = 'unknown'

        self._supported_models = ("Logger1000") #  "Logger3000", "Logger4000")
        self.device_info = {
            0x0705: { "model":"Logger3000"},
            0x0710: { "model":"Logger1000"}, 
            0x0718: { "model":"Logger4000"}
        }

        self._write_parameters: dict[str, WriteParameter] = self.logger_holding_registers.copy()

    @property
    def manufacturer(self):
        return self._manufacturer
    
    @property
    def parameters(self):
        return self._parameters
    
    @property
    def write_parameters(self):
        return self._write_parameters
    
    @property
    def supported_models(self):
        return self._supported_models


    def read_model(self, device_type_code_param_key="Device type code") -> str:
        """
            Reads model-holding register and sets self.model to its value.
            Can be used in abstractions as-is by specifying model code register name in param device_type_code_param_key
        """
        logger.info(f"Reading model for server")
        modelcode = self.read_registers(device_type_code_param_key)
        model = self.device_info[modelcode]['model']
        self.model_info = self.device_info[modelcode]

        return model

    
    def setup_valid_registers_for_model(self):
        # only support logger 1000 for now
        return
    
    def is_available(self):
        return super().is_available(register_name='Device type code')
    
    # writing should be to broadcast address of 0 on logger
    # def write_registers(self, parameter_name_slug: str, value: Any, modbus_id_override: Optional[int]=None) -> None:
    #     return super().write_registers(parameter_name_slug, value, modbus_id_override=0)

    @staticmethod
    def _decoded(registers, dtype):
        def _decode_u16(registers):
            """ Unsigned 16-bit big-endian to int """
            return registers[0]
        
        def _decode_s16(registers):
            """ Signed 16-bit big-endian to int """
            sign = 0xFFFF if registers[0] & 0x1000 else 0
            packed = struct.pack('>HH', sign, registers[0])
            return struct.unpack('>i', packed)[0]

        def _decode_u32(registers):
            """ Unsigned 32-bit mixed-endian word"""
            packed = struct.pack('>HH', registers[1], registers[0])
            return struct.unpack('>I', packed)[0]
        
        def _decode_s32(registers):
            """ Signed 32-bit mixed-endian word"""
            packed = struct.pack('>HH', registers[1], registers[0])
            return struct.unpack('>i', packed)[0]
        
        def _decode_u64(registers):
            """ Unsigned 64-bit big-endian word"""
            packed = struct.pack('>HHHH', *registers)
            return struct.unpack('>Q', packed)[0]
        
        def _decode_s64(registers):
            """ Signed 64-bit big-endian word"""
            packed = struct.pack('>HHHH', *registers)
            return struct.unpack('>q', packed)[0]

        def _decode_utf8(registers):
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.STRING)
        
        if dtype == DataType.UTF8: return _decode_utf8(registers)
        elif dtype == DataType.U16: return _decode_u16(registers)
        elif dtype == DataType.U32: return _decode_u32(registers)
        elif dtype == DataType.U64: return _decode_u64(registers)
        elif dtype == DataType.I16: return _decode_s16(registers)
        elif dtype == DataType.I32: return _decode_s32(registers)
        elif dtype == DataType.I64: return _decode_s64(registers)
        else: raise NotImplementedError(f"Data type {dtype} decoding not implemented")

    
    @staticmethod
    def _encoded(value: int, dtype: DataType) -> list[int]:
        """ Convert a float or integer to a list of big-endian 16-bit register ints.
            
            Tested on U32
        """
        # if isinstance(value, float) or isinstance(value, str):
        #     raise NotImplementedError(f"Writing floats to registers is not yet supported.")
            # Convert the float value to 4 bytes using IEEE 754 format TODO
            # value_bytes = list(struct.pack('>f', value))

        def _encode_u32(value) -> list[int]:
            """ Mixed endian unsigned 32-bit """
            high_word: int = value >> 16
            low_word: int = value & 0xFFFF
            return [low_word, high_word]
        
        if dtype == DataType.U32: return _encode_u32(int(value))
        else:
            raise ValueError(f"String decoding not suported yet. Couldn't calculate registers size.")
        
   
    def _validate_write_val(self, register_name:str, val):
        raise NotImplementedError()

if __name__ == "__main__":
    pass
    # res = SungrowLogger._encoded(32, dtype=DataType.U32)
    # print(res)
    # print(SungrowLogger._decoded(SungrowLogger, res, DataType.U32))
