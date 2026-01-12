if __name__ == "__main__":
    import sys, os
    p = os.path.abspath('modbus_mqtt')
    print(p)
    sys.path.insert(0, p)

from typing import final
from .enums import DeviceClass, HAEntityType, Parameter, RegisterTypes, DataType, WriteParameter, WriteSelectParameter
from .server import Server
from pymodbus.client import ModbusSerialClient
import struct
import logging

logger = logging.getLogger(__name__)

@final
class KehuaInverter(Server):
    """
    Inverter register map definition. Includes functions for decoding, encoding, model reading and setup of relevant register for specific models.

    """
    # Register Map
    ################################################################################################################################################
    input_registers: dict[str, Parameter]= {
        # TODO check ascii decoding; register type
        # Device and Version Information - These might be better as holding registers
        'Device Model': {'addr': 4800+1, 'count': 10, 'dtype': DataType.UTF8, 'register_type': RegisterTypes.INPUT_REGISTER, 'multiplier': 1, 'unit':'', 'device_class': DeviceClass.ENUM},
        'Hardware Version': {'addr': 4810+1, 'count': 5, 'dtype': DataType.UTF8, 'register_type': RegisterTypes.INPUT_REGISTER, 'multiplier': 1, 'unit':'', 'device_class': DeviceClass.ENUM},
        'Software Version': {'addr': 4815+1, 'count': 5, 'dtype': DataType.UTF8, 'register_type': RegisterTypes.INPUT_REGISTER, 'multiplier': 1, 'unit':'', 'device_class': DeviceClass.ENUM},
        'HMI Version': {'addr': 4820+1, 'count': 5, 'dtype': DataType.UTF8, 'register_type': RegisterTypes.INPUT_REGISTER, 'multiplier': 1, 'unit':'', 'device_class': DeviceClass.ENUM},
        'Manufacturer Info': {'addr': 4825+1, 'count': 15, 'dtype': DataType.UTF8, 'register_type': RegisterTypes.INPUT_REGISTER, 'multiplier': 1, 'unit':'', 'device_class': DeviceClass.ENUM},

        # Status Registers
        'Running Status': {'addr': 5001+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier': 1, 'unit':''},
        'Fault Code 1': {'addr': 5002+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier': 1, 'unit':''},
        'Fault Code 2': {'addr': 5003+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier': 1, 'unit':''},
        'Fault Code 3': {'addr': 5004+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier': 1, 'unit':''},
        'Fault Code 4': {'addr': 5005+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier': 1, 'unit':''},

        # Grid and Output Measurements
        'Grid Voltage U': {'addr': 5006+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Grid Voltage V': {'addr': 5007+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Grid Voltage W': {'addr': 5008+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Voltage U': {'addr': 5009+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Voltage V': {'addr': 5010+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Voltage W': {'addr': 5011+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Current U': {'addr': 5012+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'A', 'device_class': DeviceClass.CURRENT, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Current V': {'addr': 5013+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'A', 'device_class': DeviceClass.CURRENT, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Current W': {'addr': 5014+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'A', 'device_class': DeviceClass.CURRENT, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},

        # Frequencies
        'Off-Grid Frequency': {'addr': 5015+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.01, 'unit': 'Hz', 'device_class': DeviceClass.FREQUENCY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Grid Frequency': {'addr': 5016+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.01, 'unit': 'Hz', 'device_class': DeviceClass.FREQUENCY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},

        # Temperatures
        'Inner Temperature': {'addr': 5018+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': '°C', 'device_class': DeviceClass.TEMPERATURE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Radiator Temperature': {'addr': 5019+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': '°C', 'device_class': DeviceClass.TEMPERATURE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},

        # Power Measurements
        'DC Voltage': {'addr': 5020+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'DC Current': {'addr': 5021+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'A', 'device_class': DeviceClass.CURRENT, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Total DC Power': {'addr': 5022+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'kW', 'device_class': DeviceClass.POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Apparent Power': {'addr': 5023+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'kVA', 'device_class': DeviceClass.APPARENT_POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Active Power': {'addr': 5024+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'kW', 'device_class': DeviceClass.POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Output Reactive Power': {'addr': 5025+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'kVar', 'device_class': DeviceClass.REACTIVE_POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},

        # Per-Phase Power Details
        'Phase-U Apparent Power': {'addr': 5026+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'kVA', 'device_class': DeviceClass.APPARENT_POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-U Active Power': {'addr': 5027+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'kW', 'device_class': DeviceClass.POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-U Power Factor': {'addr': 5028+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.01, 'unit': '', 'device_class': DeviceClass.POWER_FACTOR, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-U Load Capacity': {'addr': 5029+1, 'count': 1, 'dtype': DataType.U16, 'unit': '%', 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement', 'device_class':DeviceClass.ENUM, 'multiplier':1},

        'Phase-V Apparent Power': {'addr': 5030+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'kVA', 'device_class': DeviceClass.APPARENT_POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-V Active Power': {'addr': 5031+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'kW', 'device_class': DeviceClass.POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-V Power Factor': {'addr': 5032+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.01, 'unit': '', 'device_class': DeviceClass.POWER_FACTOR, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-V Load Capacity': {'addr': 5033+1, 'count': 1, 'dtype': DataType.U16, 'unit': '%', 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement', 'device_class':DeviceClass.ENUM, 'multiplier':1},

        'Phase-W Apparent Power': {'addr': 5034+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'kVA', 'device_class': DeviceClass.APPARENT_POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-W Active Power': {'addr': 5035+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'kW', 'device_class': DeviceClass.POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-W Power Factor': {'addr': 5036+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.01, 'unit': '', 'device_class': DeviceClass.POWER_FACTOR, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Phase-W Load Capacity': {'addr': 5037+1, 'count': 1, 'dtype': DataType.U16, 'unit': '%', 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement', 'device_class':DeviceClass.ENUM, 'multiplier':1},

        # Energy Measurements
        'Daily Charge': {'addr': 5039+1, 'count': 2, 'dtype': DataType.U32, 'multiplier': 0.1, 'unit': 'kWh', 'device_class': DeviceClass.ENERGY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'total_increasing'},
        'Daily Discharge': {'addr': 5041+1, 'count': 2, 'dtype': DataType.U32, 'multiplier': 0.1, 'unit': 'kWh', 'device_class': DeviceClass.ENERGY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'total_increasing'},
        'Daily Gains': {'addr': 5043+1, 'count': 2, 'dtype': DataType.I32, 'unit': 'Yuan', 'device_class': DeviceClass.MONETARY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'total_increasing', 'multiplier':1},

        'Total Charge': {'addr': 5045+1, 'count': 2, 'dtype': DataType.U32, 'multiplier': 0.1, 'unit': 'kWh', 'device_class': DeviceClass.ENERGY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'total'},
        'Total Discharge': {'addr': 5047+1, 'count': 2, 'dtype': DataType.U32, 'multiplier': 0.1, 'unit': 'kWh', 'device_class': DeviceClass.ENERGY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'total'},
        'Total Gains': {'addr': 5049+1, 'count': 2, 'dtype': DataType.I32, 'unit': 'Yuan', 'device_class': DeviceClass.MONETARY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'total', 'multiplier':1},
        'Current Electricity Price': {'addr': 5051+1, 'count': 2, 'dtype': DataType.U32, 'multiplier': 0.0001, 'unit': 'Yuan', 'device_class': DeviceClass.MONETARY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},

        'Available Power': {'addr': 5054+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'kVA', 'device_class': DeviceClass.APPARENT_POWER, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Remote Control Status': {'addr': 5055+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier':1, 'unit':''},
        
        # Battery Measurements
        'BMS System Status': {'addr': 5200+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier':1, 'unit':''},
        'Total Battery Voltage': {'addr': 5202+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Total Battery Current': {'addr': 5203+1, 'count': 1, 'dtype': DataType.I16, 'multiplier': 0.1, 'unit': 'A', 'device_class': DeviceClass.CURRENT, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Battery Group SOC': {'addr': 5204+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': '%', 'device_class': DeviceClass.BATTERY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Battery Group SOH': {'addr': 5205+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': '%', 'device_class': DeviceClass.BATTERY, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Charge Limit Current': {'addr': 5206+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'A', 'device_class': DeviceClass.CURRENT, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Discharge Limit Current': {'addr': 5207+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'A', 'device_class': DeviceClass.CURRENT, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},
        'Charge Limit Voltage': {'addr': 5208+1, 'count': 1, 'dtype': DataType.U16, 'multiplier': 0.1, 'unit': 'V', 'device_class': DeviceClass.VOLTAGE, 'register_type': RegisterTypes.INPUT_REGISTER, 'state_class': 'measurement'},

        # Status and Power Availability
        'Grid Connected': {'addr': 5053+1, 'count': 1, 'dtype': DataType.U16, 'register_type': RegisterTypes.INPUT_REGISTER, 'device_class': DeviceClass.ENUM, 'multiplier':1, 'unit':''},
    }
    ################################################################################################################################################
        
    holding_parameters: dict[str, WriteParameter | WriteSelectParameter] = {
    #     "Active Power Control Mode": WriteSelectParameter(
    #     addr = 12016 + 1,
    #     count = 1,
    #     dtype = DataType.U16,
    #     multiplier = 1,
    #     register_type = RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type = HAEntityType.SELECT,
    #     options=["Disabled", "SI Control", "Percentage Control"],
    #     value_template = "{% set options = [\"Disabled\", \"SI Control\", \"Percentage Control\"] %}{% if value|int >= 0 and value|int < options|length %}{{ options[value|int] }}{% else %}{{ value }}{% endif %}",
    #     command_template = "{% set options = [\"Disabled\", \"SI Control\", \"Percentage Control\"] %}{% if value in options %}{{ options.index(value) }}{% else %}{{ value }}{% endif %}"
    # ),
    "Time Setting Hour": WriteParameter(
        addr=6023 + 1,
        count=1,
        dtype=DataType.I16,
        multiplier=1,
        register_type=RegisterTypes.HOLDING_REGISTER,
        ha_entity_type=HAEntityType.NUMBER,
        min=0,
        max=23,
        unit="",
    ),
    # "Active Power Control Percentage": WriteParameter(
    #     addr=12018 + 1,
    #     count=1,
    #     dtype=DataType.U16,
    #     multiplier=0.1,
    #     register_type=RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type=HAEntityType.NUMBER,
    #     min=0,
    #     max=100,
    #     unit="%",
    # ),
    # "Power Rate": WriteParameter(
    #     addr=12024 + 1,
    #     count=1,
    #     dtype=DataType.U16,
    #     multiplier=0.01,
    #     register_type=RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type=HAEntityType.NUMBER,
    #     min=0,
    #     max=100,
    #     unit="%/s",
    # ),
    # "OnOff Soft Start Rate": WriteParameter(
    #     addr=12025 + 1,
    #     count=1,
    #     dtype=DataType.U16,
    #     multiplier=0.01,
    #     register_type=RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type=HAEntityType.NUMBER,
    #     min=0,
    #     max=100,
    #     unit="%/s",
    # ),
        
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parameters = KehuaInverter.input_registers
        self._manufacturer = "Kehua"
        self._supported_models = ('BCS500K-A',)
        self._model = self._supported_models[0]
        self._write_parameters = KehuaInverter.holding_parameters
        # self.model = None

    @property
    def parameters(self):
        return self._parameters

    @property
    def write_parameters(self):
        return self._write_parameters
    
    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def supported_models(self):
        return self._supported_models

    def read_model(self):
        return self.read_registers("Device Model")
    
    def setup_valid_registers_for_model(self):
        """ Removes invalid registers for the specific model of inverter.
            Requires self.model. Call self.read_model() first."""
        pass

    def is_available(self):
        return super().is_available(register_name="Device Model")

    def _decode_u16(registers):
        """ Unsigned 16-bit big-endian to int """
        return registers[0]
    
    def _decode_s16(registers):
        """ Signed 16-bit big-endian to int """
        signed_values = [struct.unpack('>h', struct.pack('>H', reg))[0] for reg in registers]
        
        return signed_values[0]

    def _decode_u32(registers):
        high, low = registers
        return (high << 16) + low
    
    def _decode_s32(registers):
        # Combine two 16-bit registers into a 32-bit signed integer
        high, low = registers
        combined = (high << 16) + low
        return struct.unpack('>i', struct.pack('>I', combined))[0]

    def _decode_utf8(registers):
        return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.STRING)

    @classmethod
    def _decoded(cls, registers, dtype):
        if dtype == DataType.UTF8: return cls._decode_utf8(registers)
        elif dtype == DataType.U16: return cls._decode_u16(registers)
        elif dtype == DataType.U32: return cls._decode_u32(registers)
        elif dtype == DataType.I16: return cls._decode_s16(registers)
        elif dtype == DataType.I32: return cls._decode_s32(registers)
        else: raise NotImplementedError(f"Data type {dtype} decoding not implemented")

    @classmethod
    def _encoded(cls, value, dtype):
        """ Convert a float or integer to big-endian register.
            Supports U16 only.
        """
        # raise NotImplementedError
        def _encode_u16(value):
            """ Unsigned 16-bit big-endian to int """
            U16_MAX = 2**16-1

            if value > U16_MAX: raise ValueError(f"Cannot write {value=} to U16 register.")
            elif value < 0:     raise ValueError(f"Cannot write negative {value=} to U16 register.")

            if isinstance(value, float):
                value = int(value)
                
            return [value]

        if dtype==DataType.U16: return _encode_u16(value)
   
    # def _validate_write_val(self, register_name:str, val):
    #     """ Model-specific writes might be necessary to support more models """
    #     assert val in self.write_valid_values[register_name]

if __name__ == "__main__":
    print(KehuaInverter.input_registers)

    # def write_mqtt_migration_discovery_and_state():
    #     import pandas as pd
    #     import string

    #     valid_chars = tuple((*list(string.ascii_lowercase), '_', *[str(i) for i in range(9)]))

    #     def toalnum(s: str):
    #         if s.isalnum(): return s
            
    #         res = s.lower().replace(' ', '_').replace('.', '_').replace('-', '_').replace('(', '').replace(')', '').replace('/', '_')
    #         if not all([char in valid_chars for char in res]): print(res); assert False
    #         return res

    #     writer = pd.ExcelWriter('mqtt_migration.xlsx')

    #     entity_ids = []
    #     for name, param in KehuaInverter.input_registers.items():
            

    #         discovery_topic_new = f"homeassistant/sensor/KH1/{toalnum(name)}/config"
    #         state_topic_new = f"modbus/KH1/{toalnum(name)}"
    #         entity_ids.append((name, discovery_topic_new, state_topic_new))

    #     df = pd.DataFrame(entity_ids, columns=('name', 'discovery_topic_new', 'state_topic_new'))
    #     df.to_excel(writer, sheet_name=f'kehua')

    #     writer.close()