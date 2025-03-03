from enum import Enum

from .atess_inverter import AtessInverter

class ServerTypes(Enum):
    ATESS_INVERTER = AtessInverter
