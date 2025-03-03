from typing import final
from .server import Server
from .enums import DeviceClass, Parameter, RegisterTypes, DataType
from pymodbus.client import ModbusSerialClient
import logging

logger = logging.getLogger(__name__)


# TODO shouod be read in from registers not hard-coded
PT_RATIO = 1                        # Voltage Transfer
CT_RATIO = 320                       # Current Transfer

# Calculate actual multipliers using PT and CT ratios
VOLTAGE_MULTIPLIER = 0.1 * PT_RATIO
CURRENT_MULTIPLIER = 0.01 * CT_RATIO
POWER_MULTIPLIER = 0.001 * PT_RATIO * CT_RATIO
ENERGY_MULTIPLIER = 0.01 * PT_RATIO * CT_RATIO

@final
class AcrelMeter(Server):
    
    # subset of all registers in documentation
    # regisister definitions in document are 0-indexed. Add 1
    relevant_registers: dict[str, Parameter] = {
        "Phase A Voltage": {
            "addr": 0x0061+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "V",
            "device_class": DeviceClass.VOLTAGE,
            "multiplier": VOLTAGE_MULTIPLIER
        },
        "Phase B Voltage": {
            "addr": 0x0062+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "V",
            "device_class": DeviceClass.VOLTAGE,
            "multiplier": VOLTAGE_MULTIPLIER
        },
        "Phase C Voltage": {
            "addr": 0x0063+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "V",
            "device_class": DeviceClass.VOLTAGE,
            "multiplier": VOLTAGE_MULTIPLIER
        },
        "A-B Line Voltage": {
            "addr": 0x0078+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "V",
            "device_class": DeviceClass.VOLTAGE,
            "multiplier": VOLTAGE_MULTIPLIER
        },
        "B-C Line Voltage": {
            "addr": 0x0079+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "V",
            "device_class": DeviceClass.VOLTAGE,
            "multiplier": VOLTAGE_MULTIPLIER
        },
        "C-A Line Voltage": {
            "addr": 0x007A+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "V",
            "device_class": DeviceClass.VOLTAGE,
            "multiplier": VOLTAGE_MULTIPLIER
        },
        "Phase A Current": {
            "addr": 0x0064+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "A",
            "device_class": DeviceClass.CURRENT,
            "multiplier": CURRENT_MULTIPLIER
        },
        "Phase B Current": {
            "addr": 0x0065+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "A",
            "device_class": DeviceClass.CURRENT,
            "multiplier": CURRENT_MULTIPLIER
        },
        "Phase C Current": {
            "addr": 0x0066+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "A",
            "device_class": DeviceClass.CURRENT,
            "multiplier": CURRENT_MULTIPLIER
        },
        "Phase A Active Power": {
            "addr": 0x0164+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kW",
            "device_class": DeviceClass.POWER,
            "state_class": "measurement",
            "multiplier": POWER_MULTIPLIER
        },
        "Phase B Active Power": {
            "addr": 0x0166+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kW",
            "device_class": DeviceClass.POWER,
            "state_class": "measurement",
            "multiplier": POWER_MULTIPLIER
        },
        "Phase C Active Power": {
            "addr": 0x0168+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kW",
            "device_class": DeviceClass.POWER,
            "state_class": "measurement",
            "multiplier": POWER_MULTIPLIER
        },
        "PF": {
            "addr": 0x017F+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I16,
            "unit": "",
            "device_class": DeviceClass.POWER_FACTOR,
            "multiplier": 0.001
        },
        "Grid Frequency": {
            "addr": 0x0077+1,
            "count": 1,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.U16,
            "unit": "Hz",
            "device_class": DeviceClass.FREQUENCY,
            "multiplier": 0.01
        },
        "Active Power": {
            "addr": 0x016A+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kW",
            "device_class": DeviceClass.POWER,
            "state_class": "measurement",
            "multiplier": POWER_MULTIPLIER
        },
        "Reactive Power": {
            "addr": 0x0172+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kVar",
            "device_class": DeviceClass.REACTIVE_POWER,
            "state_class": "measurement",
            "multiplier": POWER_MULTIPLIER
        },
        "Apparent Power": {
            "addr": 0x017A+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kVA",
            "device_class": DeviceClass.APPARENT_POWER,
            "state_class": "measurement",
            "multiplier": POWER_MULTIPLIER
        },
        "Total Grid Import": {                    # was 'Forward Active Energy'
            "addr": 0x000A+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kWh",
            "device_class": DeviceClass.ENERGY,
            "multiplier": ENERGY_MULTIPLIER,
            'state_class': 'total'
        },
        "Total Grid Export": {                    # was 'Reverse Active Energy'
            "addr": 0x0014+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kWh",
            "device_class": DeviceClass.ENERGY,
            "multiplier": ENERGY_MULTIPLIER,
            'state_class': 'total'
        },
        "Forward Reactive Energy": {
            "addr": 0x0028+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kVarh",
            "device_class": DeviceClass.ENERGY,
            "multiplier": ENERGY_MULTIPLIER
        },
        "Reverse Reactive Energy": {
            "addr": 0x0032+1,
            "count": 2,
            "register_type": RegisterTypes.HOLDING_REGISTER,
            "dtype": DataType.I32,
            "unit": "kVarh",
            "device_class": DeviceClass.ENERGY,
            "multiplier": ENERGY_MULTIPLIER
        }
    }
    # write_parameters = {}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._supported_models = ('DTSD1352', ) 
        self._manufacturer = "Acrel"
        self._parameters = AcrelMeter.relevant_registers
        self._write_parameters: dict = dict()
        self.serial = 'unknown'

        self.device_info:dict | None = None

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

    def read_model(self):
        return self.supported_models[0]
    
    def setup_valid_registers_for_model(self):
        # only support logger 1000 for now
        return
    
    def is_available(self, register_name="Phase A Voltage"):
        return super().is_available(register_name=register_name)
    
    @staticmethod
    def _decoded(registers, dtype):
        def _decode_u16(registers):
            """ Unsigned 16-bit big-endian to int """
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.UINT16)
        
        def _decode_s16(registers):
            """ Signed 16-bit big-endian to int """
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.INT16)

        def _decode_u32(registers):
            """ Unsigned 32-bit big-endian word"""
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.UINT32)
        
        def _decode_s32(registers):
            """ Signed 32-bit mixed-endian word"""
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.INT32)

        def _decode_utf8(registers):
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.STRING)

        if dtype == DataType.UTF8: return _decode_utf8(registers)
        elif dtype == DataType.U16: return _decode_u16(registers)
        elif dtype == DataType.U32: return _decode_u32(registers)
        elif dtype == DataType.I16: return _decode_s16(registers)
        elif dtype == DataType.I32: return _decode_s32(registers)
        else: raise NotImplementedError(f"Data type {dtype} decoding not implemented")
        
    @staticmethod
    def _encoded(value, dtype):
        pass
   
    def _validate_write_val(self, register_name:str, val):
        raise NotImplementedError()
    

if __name__ == "__main__":
    print(AcrelMeter.__dict__)
    # server = AcrelMeter.from_config({})
    # if not server.model or not server.manufacturer or not server.serialnum or not server.nickname or not server.registers: 
