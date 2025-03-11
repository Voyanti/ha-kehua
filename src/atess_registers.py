from .enums import DataType, DeviceClass, HAEntityType, Parameter, RegisterTypes, WriteParameter, WriteSelectParameter

not_PCS_parameters: dict[str, Parameter]  = {
    # All except PCS
    "PV1 Voltage": {
        "addr": 0 + 1,
        "count": 1,
        "dtype": DataType.I16, 
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV1 DC Current": {
        "addr": 3 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV1 Power": {
        "addr": 51 + 1,
        "count": 1,
        "dtype": DataType.I16,   # Unsigned according to protocol, but observation says otherwise
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV Daily Power Generation": {
        "addr": 62 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "total_increasing"
    },
    "Total PV Generation" : {
        "addr": 64 + 1,
        "count": 2,
        "dtype": DataType.U32,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "total_increasing"
    },
}
atess_parameters: dict[str, Parameter] = {
    ###############################
    # Available on all models:
    ###############################
    "Serial Number": {
        "addr": 180 + 1,
        "count": 5,
        "dtype": DataType.UTF8,
        "device_class": DeviceClass.ENUM,
        "multiplier": 1,
        "unit": "",
        "register_type": RegisterTypes.HOLDING_REGISTER,
    },  # TODO count 5? p30
    # "Software Version": {
    #     "addr": 280 + 1,
    #     "count": 20,
    #     "dtype": DataType.UTF8,
    #     "device_class": DeviceClass.ENUM,
    #     "multiplier": 1,
    #     "unit": "",
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    "Device Type Code": {
        "addr": 43 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "device_class": DeviceClass.ENUM,
        "multiplier": 1,
        "unit": "",
        "register_type": RegisterTypes.HOLDING_REGISTER,
    }, 
    # On/Off State
    "Device On/Off": {
        "addr": 0 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 1,
        "unit": "",
        "device_class": DeviceClass.ENUM,
        "register_type": RegisterTypes.HOLDING_REGISTER,
    },
    # Voltage and Current Measurements
    "PV Voltage": { # 0 on PCS
        "addr": 80 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.HOLDING_REGISTER,
    },
    "PV Current": { # constant on PCS500
        "addr": 83 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.HOLDING_REGISTER,
    },
    "Battery Power": { # checked
        "addr": 17 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Battery SOC": { # checked
        "addr": 47 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "device_class": DeviceClass.BATTERY,
        "multiplier": 1,
        "unit": "%",
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "measurement"
    },
    # Input registers
    "Hardware Version": {
        "addr": 270 + 1,
        "count": 10,
        "dtype": DataType.UTF8,
        "device_class": DeviceClass.ENUM,
        "multiplier": 1,
        "unit": "",
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Battery Voltage": { # checked
        "addr": 1 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Battery Current": { # checked
        "addr": 2 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    ###############################
    "Ambient temperature": {
        "addr": 36 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "device_class": DeviceClass.TEMPERATURE,
        "multiplier": 0.1,
        "unit": "°C",
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    # stored as two signed 8 bit ints inside a 16 bit register:
    "BMS Max. Temperature": {
        "addr": 171 + 1,
        "count": 1,
        "dtype": DataType.I8H,
        "device_class": DeviceClass.TEMPERATURE,
        "multiplier": 1,
        "unit": "°C",
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "BMS Min. Temperature": {
        "addr": 171 + 1,
        "count": 1,
        "dtype": DataType.I8L,
        "device_class": DeviceClass.TEMPERATURE,
        "multiplier": 1,
        "unit": "°C",
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "BMS Max. Cell Voltage": { # checked
        "addr": 174 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 1,
        "unit": "mV",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "BMS Min. Cell Voltage": { # checked
        "addr": 175 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 1,
        "unit": "mV",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Total Battery Discharge Energy": { # checked
        "addr": 68 + 1,
        "count": 2,
        "dtype": DataType.U32,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "total_increasing",
    },
    "Total Battery Charge Energy": { # checked
        "addr": 72 + 1,
        "count": 2,
        "dtype": DataType.U32,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "total_increasing",
    },
}


PCS_parameters: dict[str, Parameter]  = {  # battery inverters
    "System battery current": {
        "addr": 162 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "device_class": DeviceClass.CURRENT,
        "multiplier": 0.1,
        "unit": "A",
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "System battery power": {
        "addr": 228 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "device_class": DeviceClass.POWER,
        "multiplier": 0.1,
        "unit": "kW",
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Transformer temperature": {
        "addr": 35 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "device_class": DeviceClass.TEMPERATURE,
        "multiplier": 0.1,
        "unit": "°C",
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    # "Battery Discharge Cutoff": { # 
    #     "addr": 47 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "device_class": DeviceClass.ENUM,
    #     "multiplier": 1,
    #     "unit": "%",
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    "Frequency Shift Enable": {
        "addr": 79 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "device_class": DeviceClass.ENUM,
        "multiplier": 1,
        "unit": "",
        "register_type": RegisterTypes.HOLDING_REGISTER,
    },  # 0: false, 1 = mode1, 2= mode2
    "Power factor symbol": {
        "addr": 22 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 1,
        "unit": "",
        "device_class": DeviceClass.ENUM,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Power factor": {
        "addr": 23 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.001,
        "unit": "",
        "device_class": DeviceClass.ENUM,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    # "Charge Current Limit": {
    #     "addr": 154 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "device_class": DeviceClass.CURRENT,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    #     "min": 0,
    #     "max": 10000,
    # },
    # "Discharge Current Limit": {
    #     "addr": 155 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "device_class": DeviceClass.CURRENT,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    #     "min": 0,
    #     "max": 10000,
    # },
    "Charge Cutoff SOC": {
        "addr": 178 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "device_class": DeviceClass.BATTERY,
        "multiplier": 1,
        "unit": "%",
        "register_type": RegisterTypes.HOLDING_REGISTER,
        # "min": 0,
        # "max": 100,
    },
    # PCS
    "Output Voltage UV": {
        "addr": 4 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Voltage VW": {
        "addr": 5 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Voltage WU": {
        "addr": 6 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Bypass Current U": {
        "addr": 7 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Bypass Current V": {
        "addr": 8 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Bypass Current W": {
        "addr": 9 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Inductance Current A": {
        "addr": 10 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Inductance Current B": {
        "addr": 11 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Inductance Current C": {
        "addr": 12 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },

    "Grid Bypass Voltage UV": {
        "addr": 13 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Grid Bypass Voltage VW": {
        "addr": 14 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Grid Bypass Voltage WU": {
        "addr": 15 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },

    "Bypass Frequency": {
        "addr": 81 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.01,
        "unit" : "Hz",
        "device_class": DeviceClass.FREQUENCY,
        "register_type": RegisterTypes.INPUT_REGISTER
    },


    "Output Frequency": {
        "addr": 16 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.01,
        "unit": "Hz",
        "device_class": DeviceClass.FREQUENCY,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Bypass Apparent Power": { # fout
        "addr": 18 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "",
        "device_class": DeviceClass.APPARENT_POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Bypass Active Power": { # fout
        "addr": 19 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "measurement"
    },
    "Bypass Reactive Power": { # fout
        "addr": 20 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "",
        "device_class": DeviceClass.REACTIVE_POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Grid Frequency": {
        "addr": 21 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.01,
        "unit": "Hz",
        "device_class": DeviceClass.FREQUENCY,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Grid State": {
        "addr": 28 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 1,
        "unit": "",
        "device_class": DeviceClass.ENUM,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "remarks": "0: abnormal, 1: normal"
    },
    "Output Apparent Power": {
        "addr": 78 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "",
        "device_class": DeviceClass.APPARENT_POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Active Power": {
        "addr": 79 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Reactive Power": {
        "addr": 80 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "",
        "device_class": DeviceClass.REACTIVE_POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Daily Power Consumption": { # fout
        "addr": 82 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Daily Power From Grid": { # checked
        "addr": 88 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Daily Power To Grid": { # checked
        "addr": 94 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Current U": { # checked TODO load vs output current
        "addr": 135 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Current V": { # checked
        "addr": 136 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Current W": { # checked
        "addr": 137 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    # HPS/PCS/HPSTL model registers
    "Load Apparent Power": {
        "addr": 48 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "",
        "device_class": DeviceClass.APPARENT_POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Load Active Power": {
        "addr": 49 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Load Reactive Power": {
        "addr": 50 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "",
        "device_class": DeviceClass.REACTIVE_POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Load Power Factor": {
        "addr": 52 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.001,
        "unit": "",
        "device_class": DeviceClass.POWER_FACTOR,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Load Current U": { # load current u on inverter disp
        "addr": 53 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Load Current V": {# load current v on inverter disp
        "addr": 54 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Load Current W": {# load current w on inverter disp
        "addr": 55 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Voltage U": {
        "addr": 56 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Voltage V": {
        "addr": 57 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Voltage W": {
        "addr": 58 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Total Grid Import" : {
        "addr": 90 + 1,
        "count": 2,
        "dtype": DataType.U32,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "total"
    },
    "Total Grid Export" : {
        "addr": 96 + 1,
        "count": 2,
        "dtype": DataType.U32,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "total"
    },
    "Total Load Energy": {
        "addr": 84 + 1,
        "count": 2,
        "dtype": DataType.U32,
        "multiplier": 0.1,
        "unit": "kWh",
        "device_class": DeviceClass.ENERGY,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "state_class": "total"
    },
    "BMS Battery Status": {
        "addr": 176 + 1,
        "count": 1,
        "dtype": DataType.I8H,
        "multiplier": 1,
        "unit": "",
        "device_class": DeviceClass.ENUM,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "value_template": """
                            {% set states = {
                            '0': 'Hold',
                            '1': 'Charging and discharging disable',
                            '2': 'Charging disable',
                            '3': 'Discharging disable',
                            '4': 'Charging',
                            '5': 'Discharging'
                            } %}
                            {{ states[value] if value in states else 'unknown' }}
                            """
    },
    "BMS System Status": {
        "addr": 176 + 1,
        "count": 1,
        "dtype": DataType.I8L,
        "multiplier": 1,
        "unit": "",
        "device_class": DeviceClass.ENUM,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Running State": {
        "addr": 180 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 1,
        "unit": "",
        "device_class": DeviceClass.ENUM,
        "register_type": RegisterTypes.INPUT_REGISTER,
        "value_template": """
                        {% set states = {
                        '0': 'Waiting',
                        '1': 'Inspection',
                        '2': 'On-Grid',
                        '3': 'Fault',
                        '4': 'Permanentfault',
                        '5': 'Off-Grid',
                        '6': 'Single PV mode',
                        '7': 'Switch-to-off-grid',
                        '8': 'Switch-to-on-grid'
                        } %}
                        {{ states[value] if value in states else 'unknown' }}
                        """
    },

}
# TODO bypass p 37 atess-modbus-rtu-protocol-v37.pdf

PBD_parameters: dict[str, Parameter]  = {
    
    # PBD
    "PV2 Voltage": {
        "addr": 105 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV2 DC Current": {
        "addr": 106 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV2 Power": {
        "addr": 107 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV Total Power": {
        "addr": 108 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Voltage": {
        "addr": 109 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Current": {
        "addr": 110 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "Output Power": {
        "addr": 113 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV Module Temperature": { # 0 on PCS
        "addr": 114 + 1,
        "count": 1,
        "dtype": DataType.U16,
        "multiplier": 0.1,
        "unit": "°C",
        "device_class": DeviceClass.TEMPERATURE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV3 Voltage": {
        "addr": 123 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV4 Voltage": {
        "addr": 124 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV5 Voltage": {
        "addr": 125 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "V",
        "device_class": DeviceClass.VOLTAGE,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV3 DC Current": {
        "addr": 126 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV4 DC Current": {
        "addr": 127 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV5 DC Current": {
        "addr": 128 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "A",
        "device_class": DeviceClass.CURRENT,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV3 Power": {
        "addr": 132 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV4 Power": {
        "addr": 133 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
    "PV5 Power": {
        "addr": 134 + 1,
        "count": 1,
        "dtype": DataType.I16,
        "multiplier": 0.1,
        "unit": "kW",
        "device_class": DeviceClass.POWER,
        "register_type": RegisterTypes.INPUT_REGISTER,
    },
}

# Atess Modbus RTU v3.22 p127 fig 4.1.2 
# register 43: Device Type Code -> str
model_code_to_name: dict[int, str] = {
    22001: "HPS30",
    22002: "HPS50",
    22003: "HPS100",
    22004: "HPS120",
    22005: "HPS150",
    22006: "HPS250",
    22007: "HPS7500TL",
    22008: "HPS20KTL",
    22009: "HPS10KTL",
    22010: "HPS10KTLS",
    22011: "HPS7500TLS",
    22012: "HPS5KTLS",
    22013: "HPS3500TLS",
    22014: "HPS20KTLS",
    22015: "HPS15KTL",
    22016: "HPS30KTL",
    22017: "HPS40KTL",
    21016: "PCS50",
    21017: "PCS50TL",
    21018: "PCS50U",
    21019: "PCS100",
    21020: "PCS100TL",
    21021: "PCS100U",
    21022: "PCS250",
    21023: "PCS250TL",
    21024: "PCS250U",
    21025: "PCS500",
    21026: "PCS500TL",
    21027: "PCS500U",
    21028: "PCS50 (new model)",
    21029: "PCS50TL",
    21030: "PCS50U",
    21031: "PCS100",
    21032: "PCS100TL",
    21033: "PCS100U",
    21034: "PCS250",
    21035: "PCS250TL",
    21036: "PCS250U",
    21037: "PCS500",
    21038: "PCS500TL",
    21039: "PCS500U",
    21040: "PCS630",
    23001: "PBD350 (old model)",
    23002: "PBD350 (new model)",
    23003: "PBD250",
}

atess_write_parameters: dict[str, WriteParameter | WriteSelectParameter] = {
    "Mode selection": WriteSelectParameter( # ALL
        addr = 26 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.SELECT,
        options=["Load First", "Battery First", "Economy Mode", "Peak Shaving", "Time Schedule", "Manual Dispatch", "Battery Protect", "Backup Power Management", "Constant Power Discharge", "Forced Charging", "Smart Meter Mode", "Bat-Smart Meter"],
        value_template = "{% set options = [\"Load First\", \"Battery First\", \"Economy Mode\", \"Peak Shaving\", \"Time Schedule\", \"Manual Dispatch\", \"Battery Protect\", \"Backup Power Management\", \"Constant Power Discharge\", \"Forced Charging\", \"Smart Meter Mode\", \"Bat-Smart Meter\"] %}{% if value|int >= 0 and value|int < options|length %}{{ options[value|int] }}{% else %}{{ value }}{% endif %}",
        command_template = "{% set options = [\"Load First\", \"Battery First\", \"Economy Mode\", \"Peak Shaving\", \"Time Schedule\", \"Manual Dispatch\", \"Battery Protect\", \"Backup Power Management\", \"Constant Power Discharge\", \"Forced Charging\", \"Smart Meter Mode\", \"Bat-Smart Meter\"] %}{% if value in options %}{{ options.index(value) }}{% else %}{{ value }}{% endif %}"
    ),
    "Bypass Cabinet Enable": WriteParameter( # PCS
        addr = 13 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.SWITCH,
        payload_off = 0,
        payload_on = 1,
    ),
    "BMS Communication Enable": WriteParameter( # PCS
        addr = 14 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.SWITCH,
        payload_off = 0,
        payload_on = 1,
    ),

    # Battery. NOTE Actually all types have this holding register
    "Generator Start SOC": WriteParameter( # ALL "SOC Up Limit" # When off-grid AND in diesel Generator (DG) mode
        addr = 66 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 100,
        unit = "%",
    ), 
    "Grid Power Compensation": WriteParameter( # ALL
        addr = 44 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 0.1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 100,
        unit = "kW",
    ), 
    "Generator Stop SOC": WriteParameter( # ALL
        addr = 67 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 100,
        unit = "%",
    ), 
    "BMS Max Charge Current": WriteParameter( # ALL
        addr = 100 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 0.1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 1000,
        unit = "A",
    ), 
    "BMS Max Discharge Current": WriteParameter( # ALL
        addr = 101 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 0.1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 1000,
        unit = "A",
    ), 
    "Battery Charging Saturation": WriteParameter( # ALL
        addr = 150 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 10,
    ), 


    "Charge Cutoff SOC": WriteParameter( # ALL
        addr = 178 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 100,
        unit = "%",
    ), 
    "Discharge Cutoff SOC": WriteParameter( # ALL
        addr = 47 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 100,
        unit = "%",
    ), 
    "Grid Charge Cutoff SOC": WriteParameter( # ALL
        addr = 340 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 100,
        unit = "%",
    ), 
    "Battery Power Export to Grid Set": WriteParameter( # ALL
        addr = 174 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 150,
        unit = "kW",
    ), 

    "Grid And PV Charge Together": WriteParameter( # ALL
        addr = 8 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.SWITCH,
        payload_off = 0,
        payload_on = 1,
    ), 
    "Max Grid Charge Power": WriteParameter( # ALL
        addr = 225 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 0.1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        min = 0,
        max = 150, # TODO
        unit = "kW",
    ), 
    "Forced Charge Enable": WriteParameter( # ALL
        addr = 229 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.SWITCH,
        payload_off = 0,
        payload_on = 1,
    ),
    "Anti Reflux Enable": WriteParameter( # HPS, PCS, HPSTL
        addr = 16 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.SWITCH,
        payload_off = 0,
        payload_on = 1,
    ),
    # "PV Power Limit": WriteParameter( # ALL # "PV power setting"
    #     addr = 33 + 1,
    #     count = 1,
    #     dtype = DataType.U16,
    #     multiplier = 1,
    #     register_type = RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type = HAEntityType.NUMBER,
    #     unit="kW",
    #     min = 0,
    #     max = 500
    # ), 
    "Output Power Limit": WriteParameter( # ALL # "Output Power Upper Limit"
        addr = 58 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        unit="%",
        min = 0,
        max = 120
    ), 
    # "Load Power Limit": WriteParameter( # ALL # "Output Power Upper Limit"
    #     addr = 107 + 1,
    #     count = 1,
    #     dtype = DataType.U16,
    #     multiplier = 1,
    #     register_type = RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type = HAEntityType.NUMBER,
    #     unit="kW",
    #     min = 0,
    #     max = 500
    # ), 
    "Grid Power UP Limit": WriteParameter( # ALL # "Grid Power UP Limit"
        addr = 65 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        unit="kW",
        min = 0,
        max = 500
    ), 
    # "Max Grid Import Power": WriteParameter( # ALL # "Upper limit powerfeed from grid"
    #     addr = 169 + 1,
    #     count = 1,
    #     dtype = DataType.U16,
    #     multiplier = 1,
    #     register_type = RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type = HAEntityType.NUMBER,
    #     unit="kW",
    #     min = 0,
    #     max = 500
    # ), 
    "Discharge current limit": WriteParameter( # ALL # "Upper limit powerfeed from grid"
        addr = 155 + 1,
        count = 1,
        dtype = DataType.U16,
        multiplier = 0.1,
        register_type = RegisterTypes.HOLDING_REGISTER,
        ha_entity_type = HAEntityType.NUMBER,
        unit="A",
        min = 0,
        max = 1000 # TODO "10000"
    ), 
    # "Battery Discharge Current HPS": WriteParameter( # HPS # "Upper limit powerfeed from grid"
    #     addr = 172 + 1,
    #     count = 1,
    #     dtype = DataType.U16,
    #     multiplier = 1,
    #     register_type = RegisterTypes.HOLDING_REGISTER,
    #     ha_entity_type = HAEntityType.NUMBER,
    #     unit="A",
    #     min = 0,
    #     max = 1000 # TODO "10000"
    # ), 
}


deprecated: dict[str, Parameter]= {
    # Voltage and Current Measurements
    # "PV Voltage Calibration": {
    #     "addr": 80 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Battery Voltage Calibration": {
    #     "addr": 81 + 1,
    #     "count": 1,
    #     "dtype": DataType.I16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Battery Current Calibration": {
    #     "addr": 82 + 1,
    #     "count": 1,
    #     "dtype": DataType.I16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "PV Current Calibration": {
    #     "addr": 83 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # Output Voltages
    # "Output Voltage U Calibration": {
    #     "addr": 84 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Output Voltage V Calibration": {
    #     "addr": 85 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Output Voltage W Calibration": {
    #     "addr": 86 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # Grid Currents
    # "Grid Current U Calibration": {
    #     "addr": 87 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Grid Current V Calibration": {
    #     "addr": 88 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Grid Current W Calibration": {
    #     "addr": 89 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # Grid Voltages
    # "Grid Voltage UV Calibration": {
    #     "addr": 90 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Grid Voltage VW Calibration": {
    #     "addr": 91 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Grid Voltage WU Calibration": {
    #     "addr": 92 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "V",
    #     "device_class": DeviceClass.VOLTAGE,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # Load Currents
    # "Load Current U Calibration": {
    #     "addr": 93 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Load Current V Calibration": {
    #     "addr": 94 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
    # "Load Current W Calibration": {
    #     "addr": 95 + 1,
    #     "count": 1,
    #     "dtype": DataType.U16,
    #     "multiplier": 0.1,
    #     "unit": "A",
    #     "device_class": DeviceClass.CURRENT,
    #     "register_type": RegisterTypes.HOLDING_REGISTER,
    # },
}

if __name__ == "__main__":
    def create_batches(parameters: dict[str, Parameter | WriteParameter | WriteSelectParameter]):
        holding_params = [(k, v) for k, v in parameters.items() if v["register_type"] == RegisterTypes.HOLDING_REGISTER]
        input_params = [(k, v) for k, v in parameters.items() if v["register_type"] == RegisterTypes.INPUT_REGISTER]

        for params in (holding_params, input_params):
            params = sorted(params, key=lambda x: x[1]["addr"])
            print([i[1]["addr"] for i in params])


    def find_consecutive_groups(numbers):
        """
        Find groups of consecutive numbers in a list.
        
        Args:
            numbers: A list of integers
            
        Returns:
            A list of lists, where each inner list is a group of consecutive numbers
        """
        if not numbers:
            return []
        
        # Sort the input list
        numbers = sorted(numbers)
        
        # Initialize the result and the first group
        result = []
        current_group = [numbers[0]]
        
        # Iterate through the rest of the numbers
        for i in range(1, len(numbers)):
            # If the current number is consecutive to the previous one
            if numbers[i] == numbers[i-1] + 1:
                current_group.append(numbers[i])
            # If not consecutive and not a duplicate
            elif numbers[i] != numbers[i-1]:
                # Save the current group if it's not empty
                if current_group:
                    result.append(current_group)
                # Start a new group
                current_group = [numbers[i]]
        
        # Add the last group if it's not empty
        if current_group:
            result.append(current_group)
        
        return result

    # # Your two lists
    # list1 = [1, 9, 14, 15, 17, 27, 44, 45, 48, 59, 66, 67, 68, 80, 81, 84, 101, 102, 151, 156, 175, 179, 181, 226, 230, 341]
    # list2 = [2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 29, 36, 37, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59, 69, 73, 79, 80, 81, 82, 83, 85, 89, 91, 95, 97, 136, 137, 138, 163, 172, 172, 175, 176, 177, 177, 181, 229, 271]

    # # Find the consecutive groups in each list
    # groups_list1 = find_consecutive_groups(list1)
    # groups_list2 = find_consecutive_groups(list2)

    # # Print the results
    # print("Consecutive groups in list1:")
    # for i, group in enumerate(groups_list1):
    #     print(f"Group {i+1}: {group}")

    # print("\nConsecutive groups in list2:")
    # for i, group in enumerate(groups_list2):
    #     print(f"Group {i+1}: {group}")

    # # Count the number of groups in each list
    # print(f"\nNumber of consecutive groups in list1: {len(groups_list1)}")
    # print(f"Number of consecutive groups in list2: {len(groups_list2)}")

    params: dict[str, Parameter | WriteParameter | WriteSelectParameter] = atess_parameters.copy()
    # params.update(PCS_parameters)
    params.update(PBD_parameters)
    params.update(not_PCS_parameters)
    # params.update(atess_write_parameters)
    create_batches(params)