from enum import Enum
from kehua_inverter import KehuaInverter

# Declare all defined server abstractions here. Add to schema in config.yaml to enable selecting.
class ServerTypes(Enum):
    KEHUA_INVERTER = KehuaInverter
    