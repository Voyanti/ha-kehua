from enum import Enum

from .sungrow_inverter import SungrowInverter
from .sungrow_logger import SungrowLogger
from .sungrow_meter import AcrelMeter

# Declare all defined server abstractions here. Add to schema in config.yaml to enable selecting.


class ServerTypes(Enum):
    SUNGROW_INVERTER = SungrowInverter
    SUNGROW_LOGGER = SungrowLogger
    SUNGROW_METER = AcrelMeter
