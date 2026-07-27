import unittest
from src.loader import *
from src.options import *


class TestLoaders(unittest.TestCase):
    def setUp(self):
        self.yaml_path = "config.yaml"

    # Validaters
    def test_validate_names_raises(self):
        with self.assertRaisesRegex(
            ValueError, "Device/ Client names must be unique"
        ) as cm:
            validate_names(["asdf", "asdf", "as"])

        with self.assertRaisesRegex(
            ValueError, "names must be alphanumeric"
        ) as cm:
            validate_names(["A*"])

    def test_validate_names_not_raise(self):
        validate_names(["asDf", "asd1", "as"])

    # Loader
    def test_loader(self):
        """
        TODO Maybe not reading the specified path.."""
        self.assertIsInstance(load_options(
            json_rel_path=self.yaml_path), AppOptions)

    # Load and Validate
    def test_load_validate(self):
        """
        Test passing of arguments from options to validaters. """
        self.assertIsInstance(load_validate_options(
            json_rel_path=self.yaml_path), AppOptions)

    # Implemented Server Validator
    def test_validate_server_implemented(self):
        """
        Tests that the server name set in config.yaml/.json is implemented and defined in implemented_servers.py
        Assumes load_options works"""
        try:
            OPTS = load_options(self.yaml_path)
            servers = OPTS.servers
        except Exception as e:
            print(
                "Error while reading options as prerequisite for validate_servers_implemented"
            )
            raise e

        validate_server_implemented(servers)

    # Rounding overrides
    def test_validate_rounding_overrides_raises(self):
        with self.assertRaisesRegex(ValueError, "not a valid Home Assistant device class"):
            validate_rounding_overrides([RoundingOption("powr", 1)])

        with self.assertRaisesRegex(ValueError, "must be in 0..6"):
            validate_rounding_overrides([RoundingOption("power", 9)])

        with self.assertRaisesRegex(ValueError, "Duplicate rounding override"):
            validate_rounding_overrides(
                [RoundingOption("power", 0), RoundingOption("power", 1)]
            )

    def test_validate_rounding_overrides_not_raise(self):
        validate_rounding_overrides([])
        validate_rounding_overrides([RoundingOption("power", 0), RoundingOption("energy", 2)])

    def test_build_rounding_map_overrides_defaults(self):
        """Overrides win; unlisted device classes keep their built-in default."""
        opts = load_options(self.yaml_path)
        opts.rounding_overrides = [RoundingOption("power", 3)]

        rounding = build_rounding_map(opts)

        self.assertEqual(rounding[DeviceClass.POWER], 3)
        self.assertEqual(
            rounding[DeviceClass.CURRENT], device_class_to_rounding[DeviceClass.CURRENT]
        )
        # defaults must not be mutated
        self.assertNotEqual(device_class_to_rounding[DeviceClass.POWER], 3)


if __name__ == "__main__":
    unittest.main()
