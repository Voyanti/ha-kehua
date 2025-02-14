import unittest
from kehua_inverter import KehuaInverter

class TestKehuaInverter(unittest.TestCase):

    def test_decode_u16(self):
        # 0x0102 -> 258
        self.assertEqual(KehuaInverter._decode_u16([258, ]), 258)

    def test_decode_u32(self):
        # 0x01020304 -> 16909060
        self.assertEqual(KehuaInverter._decode_u32([772, 258]), 16909060)

    def test_decode_utf8(self):
        # UTF-8 string represented as a sequence of registers
        self.assertEqual(KehuaInverter._decode_utf8([16706, 17220, 17734, 18248, 18762]), "ABCDEFGHIJ")

    def test_decode_s16(self):
        # 2**15-1 == -32769
        self.assertEqual(KehuaInverter._decode_s16([32768 - 1]), -32769)
        # 2**16-1 == -1
        self.assertEqual(KehuaInverter._decode_s16([2**16 - 1]), -1)

    def test_decode_s32(self):
        # 2**32-1 == -1
        self.assertEqual(KehuaInverter._decode_s32([65535, 65535]), -1)

    def test_decode_s32_alternate(self):
        # 0xFFFF777B -> -34949
        self.assertEqual(KehuaInverter._decode_s32([30587, 65535]), -34949)

    def test_encode_working(self):
        self.assertEqual(KehuaInverter._encoded(2**16-1), [0, 0, 255, 255])
        # self.assertEqual(KehuaInverter._encoded(float(2**16-1)), [0, 0, 255, 255])      # is_float
        self.assertEqual(KehuaInverter._encoded(0), [0, 0, 0, 0])
        
    def test_encode_breaking(self):
        self.assertRaisesRegex(ValueError, r"ValueError: Cannot write negative value=(-?\d+) to U16 register\.", KehuaInverter._encoded(-1))
        self.assertRaises(ValueError, r"ValueError: Cannot write negative value=(-?\d+) to U16 register\.", KehuaInverter._encoded(2**16))

    # def test_setup_valid_register_for_model(self):
    #     c = KehuaInverter(name="Sungrow Inverter 1",
    #                         nickname="SG1", 
    #                         serialnum="1234",
    #                         device_addr=1)
    #     c.model = "SG80KTL-20"

    #     c.setup_valid_registers_for_model()

    #     should_not_contain = [
    #         'Total Apparent Power', 'Total Power Yields (Increased Accuracy)', 'Grid Frequency (Increased Accuracy)', 'PID Work State',
    #         'Export power limitation', 'Export power limitation value'
    #     ]
    #     for item in should_not_contain:
    #         self.assertNotIn(item, c.registers)
        