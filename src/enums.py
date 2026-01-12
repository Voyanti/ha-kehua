from enum import Enum
from typing import Literal, Optional, Any, TypedDict
from typing import FrozenSet, Dict


class RegisterTypes(Enum):
    INPUT_REGISTER = 3  # Read Only
    HOLDING_REGISTER = 4  # Read/ Write


class DataType(Enum):
    """
    Data types used by server registers. Used to choose decoding method. depending op server.
    """
    # Individual Bit
    B17 = "B17"

    # Unsigned integers
    U16 = "U16"
    U32 = "U32"
    U64 = "U64"

    # Signed integers
    I8L = "I8L"
    I8H = "I8H"
    I16 = "I16"
    I32 = "I32"
    I64 = "I64"

    # Floats
    F32 = "F32"
    F64 = "F64"

    # String
    UTF8 = "UTF8"

    @property
    def size(self) -> Optional[int]:
        """
        Returns the size in bytes for fixed-size types.
        Returns None for variable-size types (UTF8).
        """
        sizes = {
            DataType.U16: 2,
            DataType.I16: 2,
            DataType.U32: 4,
            DataType.I32: 4,
            DataType.F32: 4,
            DataType.F32: 4,
            DataType.U64: 8,
            DataType.I64: 8,
            DataType.UTF8: None,
        }
        return sizes[self]

    @property
    def min_value(self) -> Optional[int]:
        """Returns the minimum value for numeric types."""
        ranges = {
            DataType.I8L: -128,  # -2^7
            DataType.I8H: -128,  # -2^7
            DataType.U16: 0,
            DataType.U32: 0,
            DataType.I16: -32768,  # -2^15
            DataType.I32: -2147483648,  # -2^31
            DataType.U64: 0,
            DataType.I64: -18446744073709551616,
            DataType.UTF8: None,
        }
        return ranges[self]

    @property
    def max_value(self) -> Optional[int]:
        """Returns the maximum value for numeric types."""
        ranges = {
            DataType.I8L: 127,  # 2^7-1
            DataType.I8H: 127,  # 2^7-1
            DataType.U16: 65535,  # 2^16 - 1
            DataType.U32: 4294967295,  # 2^32 - 1
            DataType.I16: 32767,  # 2^15 - 1
            DataType.I32: 2147483647,  # 2^31 - 1
            DataType.U64: 18446744073709551615,
            DataType.I64: 9223372036854775807,
            DataType.UTF8: None,
        }
        return ranges[self]


# https://www.home-assistant.io/integrations/sensor#device-class



class DeviceClass(Enum):
    # time/text
    DATE = "date"
    ENUM = "enum"
    TIMESTAMP = "timestamp"

    # environment, phys. quantities
    ABSOLUTE_HUMIDITY = "absolute_humidity"
    APPARENT_POWER = "apparent_power"
    AQI = "aqi"
    AREA = "area"
    ATMOSPHERIC_PRESSURE = "atmospheric_pressure"
    BATTERY = "battery"
    BLOOD_GLUCOSE_CONCENTRATION = "blood_glucose_concentration"
    CARBON_DIOXIDE = "carbon_dioxide"
    CARBON_MONOXIDE = "carbon_monoxide"
    CURRENT = "current"
    DATA_RATE = "data_rate"
    DATA_SIZE = "data_size"
    DISTANCE = "distance"
    DURATION = "duration"
    ENERGY = "energy"
    ENERGY_DISTANCE = "energy_distance"
    ENERGY_STORAGE = "energy_storage"
    FREQUENCY = "frequency"
    GAS = "gas"
    HUMIDITY = "humidity"
    ILLUMINANCE = "illuminance"
    IRRADIANCE = "irradiance"
    MOISTURE = "moisture"
    MONETARY = "monetary"
    NITROGEN_DIOXIDE = "nitrogen_dioxide"
    NITROGEN_MONOXIDE = "nitrogen_monoxide"
    NITROUS_OXIDE = "nitrous_oxide"
    OZONE = "ozone"
    PH = "ph"
    PM1 = "pm1"
    PM25 = "pm25"
    PM10 = "pm10"
    POWER_FACTOR = "power_factor"
    POWER = "power"
    PRECIPITATION = "precipitation"
    PRECIPITATION_INTENSITY = "precipitation_intensity"
    PRESSURE = "pressure"
    REACTIVE_ENERGY = "reactive_energy"
    REACTIVE_POWER = "reactive_power"
    SIGNAL_STRENGTH = "signal_strength"
    SOUND_PRESSURE = "sound_pressure"
    SPEED = "speed"
    SULPHUR_DIOXIDE = "sulphur_dioxide"
    TEMPERATURE = "temperature"
    VOLATILE_ORGANIC_COMPOUNDS = "volatile_organic_compounds"
    VOLATILE_ORGANIC_COMPOUNDS_PARTS = "volatile_organic_compounds_parts"
    VOLTAGE = "voltage"
    VOLUME = "volume"
    VOLUME_STORAGE = "volume_storage"
    VOLUME_FLOW_RATE = "volume_flow_rate"
    WATER = "water"
    WEIGHT = "weight"
    WIND_DIRECTION = "wind_direction"
    WIND_SPEED = "wind_speed"

device_class_to_rounding: dict[DeviceClass, int] = { 
        DeviceClass.REACTIVE_POWER: 0,
        DeviceClass.ENERGY: 1,
        DeviceClass.FREQUENCY: 1,
        DeviceClass.POWER_FACTOR: 1,
        DeviceClass.APPARENT_POWER: 0, 
        DeviceClass.CURRENT: 1,
        DeviceClass.VOLTAGE: 0,
        DeviceClass.POWER: 0
    }

# Exact valid units per HA docs (empty set => unitless/text)
VALID_UNITS: Dict[DeviceClass, FrozenSet[str]] = {
    DeviceClass.DATE: frozenset(),
    DeviceClass.ENUM: frozenset(),
    DeviceClass.TIMESTAMP: frozenset(),

    DeviceClass.ABSOLUTE_HUMIDITY: frozenset({"g/m³", "mg/m³"}),
    DeviceClass.APPARENT_POWER: frozenset({"VA"}),
    DeviceClass.AQI: frozenset(),
    DeviceClass.AREA: frozenset({"m²", "cm²", "km²", "mm²", "in²", "ft²", "yd²", "mi²", "ac", "ha"}),
    DeviceClass.ATMOSPHERIC_PRESSURE: frozenset({"cbar", "bar", "hPa", "mmHg", "inHg", "kPa", "mbar", "Pa", "psi"}),
    DeviceClass.BATTERY: frozenset({"%"}),
    DeviceClass.BLOOD_GLUCOSE_CONCENTRATION: frozenset({"mg/dL", "mmol/L"}),
    DeviceClass.CARBON_DIOXIDE: frozenset({"ppm"}),
    DeviceClass.CARBON_MONOXIDE: frozenset({"ppm"}),
    DeviceClass.CURRENT: frozenset({"A", "mA"}),
    DeviceClass.DATA_RATE: frozenset({"bit/s", "kbit/s", "Mbit/s", "Gbit/s", "B/s", "kB/s", "MB/s", "GB/s", "KiB/s", "MiB/s", "GiB/s"}),
    DeviceClass.DATA_SIZE: frozenset({"bit","kbit","Mbit","Gbit","B","kB","MB","GB","TB","PB","EB","ZB","YB","KiB","MiB","GiB","TiB","PiB","EiB","ZiB","YiB"}),
    DeviceClass.DISTANCE: frozenset({"km","m","cm","mm","mi","nmi","yd","in"}),
    DeviceClass.DURATION: frozenset({"d","h","min","s","ms","µs"}),
    DeviceClass.ENERGY: frozenset({"J","kJ","MJ","GJ","mWh","Wh","kWh","MWh","GWh","TWh","cal","kcal","Mcal","Gcal"}),
    DeviceClass.ENERGY_DISTANCE: frozenset({"kWh/100km","Wh/km","mi/kWh","km/kWh"}),
    DeviceClass.ENERGY_STORAGE: frozenset({"J","kJ","MJ","GJ","mWh","Wh","kWh","MWh","GWh","TWh","cal","kcal","Mcal","Gcal"}),
    DeviceClass.FREQUENCY: frozenset({"Hz","kHz","MHz","GHz"}),
    DeviceClass.GAS: frozenset({"L","m³","ft³","CCF"}),
    DeviceClass.HUMIDITY: frozenset({"%"}),
    DeviceClass.ILLUMINANCE: frozenset({"lx"}),
    DeviceClass.IRRADIANCE: frozenset({"W/m²","BTU/(h⋅ft²)"}),
    DeviceClass.MOISTURE: frozenset({"%"}),
    DeviceClass.MONETARY: frozenset(),  # ISO 4217 currency codes (free text like "USD","EUR")
    DeviceClass.NITROGEN_DIOXIDE: frozenset({"µg/m³"}),
    DeviceClass.NITROGEN_MONOXIDE: frozenset({"µg/m³"}),
    DeviceClass.NITROUS_OXIDE: frozenset({"µg/m³"}),
    DeviceClass.OZONE: frozenset({"µg/m³"}),
    DeviceClass.PH: frozenset(),
    DeviceClass.PM1: frozenset({"µg/m³"}),
    DeviceClass.PM25: frozenset({"µg/m³"}),
    DeviceClass.PM10: frozenset({"µg/m³"}),
    DeviceClass.POWER_FACTOR: frozenset(),  # unitless, may be expressed as % in UI
    DeviceClass.POWER: frozenset({"mW","W","kW","MW","GW","TW"}),
    DeviceClass.PRECIPITATION: frozenset({"cm","in","mm"}),
    DeviceClass.PRECIPITATION_INTENSITY: frozenset({"in/d","in/h","mm/d","mm/h"}),
    DeviceClass.PRESSURE: frozenset({"Pa","kPa","hPa","bar","cbar","mbar","mmHg","inHg","psi"}),
    DeviceClass.REACTIVE_ENERGY: frozenset({"varh","kvarh"}),
    DeviceClass.REACTIVE_POWER: frozenset({"var","kvar"}),
    DeviceClass.SIGNAL_STRENGTH: frozenset({"dB","dBm"}),
    DeviceClass.SOUND_PRESSURE: frozenset({"dB","dBA"}),
    DeviceClass.SPEED: frozenset({"ft/s","in/d","in/h","in/s","km/h","kn","m/s","mph","mm/d","mm/s"}),
    DeviceClass.SULPHUR_DIOXIDE: frozenset({"µg/m³"}),
    DeviceClass.TEMPERATURE: frozenset({"°C","°F","K"}),
    DeviceClass.VOLATILE_ORGANIC_COMPOUNDS: frozenset({"µg/m³","mg/m³"}),
    DeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS: frozenset({"ppm","ppb"}),
    DeviceClass.VOLTAGE: frozenset({"V","mV","µV","kV","MV"}),
    DeviceClass.VOLUME: frozenset({"L","mL","gal","fl. oz.","m³","ft³","CCF"}),
    DeviceClass.VOLUME_FLOW_RATE: frozenset({"m³/h","m³/s","ft³/min","L/h","L/min","L/s","gal/min","mL/s"}),
    DeviceClass.VOLUME_STORAGE: frozenset({"L","mL","gal","fl. oz.","m³","ft³","CCF"}),
    DeviceClass.WATER: frozenset({"L","gal","m³","ft³","CCF"}),
    DeviceClass.WEIGHT: frozenset({"kg","g","mg","µg","oz","lb","st"}),
    DeviceClass.WIND_DIRECTION: frozenset({"°"}),
    DeviceClass.WIND_SPEED: frozenset({"Beaufort","ft/s","km/h","kn","m/s","mph"}),
}

class HAEntityType(Enum):
    NUMBER = 'number'
    SWITCH = 'switch'
    SELECT = 'select'

    SENSOR = 'sensor'
    BINARY_SENSOR = 'binary_sensor'

# all parameters are required to have these fields
ParameterReq = TypedDict(
    "ParameterReq",
    {
        "addr": int,
        "count": int,
        "dtype": DataType,
        "multiplier": float,
        "unit": str,
        "device_class": DeviceClass | None,
        "register_type": RegisterTypes,
    },
)

# inherit required parameters, add optional parameters
class Parameter(ParameterReq, total=False):
    remarks: str
    state_class: Literal["measurement", "total", "total_increasing"]
    value_template: str

    # all oarameters are required to have these fields
WriteParameterReq = TypedDict(
    "WriteParameterReq",
    {
        "addr": int,
        "count": int,
        "dtype": DataType,
        "multiplier": float,
        "register_type": RegisterTypes,
        'ha_entity_type': HAEntityType,
    },
)

class WriteSelectParameterReq(WriteParameterReq, total=True):
    # select
    options: list[str] # required for select

class WriteSelectParameter(WriteSelectParameterReq, total=False):
    value_template: str
    command_template: str
    
class WriteParameter(WriteParameterReq, total=False):
    device_class: DeviceClass # when not specified w=for a switch, a none type switch is used

    # number
    unit: str
    min: float  
    max: float

    # switch
    payload_off: int
    payload_on: int

    

if __name__ == "__main__":
    print(DataType.U16.min_value)
