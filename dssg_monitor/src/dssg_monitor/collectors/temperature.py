from prometheus_client import Gauge


class DS18B20Reader:
    """Class to read temperature from DS18B20 devices."""

    def __init__(self, address, name):
        """Access temperature file and initialise metric gauge.
        
        kwargs:
        address -- File path to sensor
        """
        self.name = name
        self.addr = str(address)
        self.temp_addr = self.addr + "/temperature"
        self.temp_file = open(self.temp_addr)
        self.temp_gauge = Gauge(("temp_" + self.name), 'Temperature reading on DS18B20')

    def read_temp(self):
        """Read current temperature."""
        self.temp_file.seek(0)
        data = self.temp_file.read()[:-1]
        self.temp_gauge.set(int(data) / 1000)


class BME280Reader:
    """Class to read temperature from BME280 devices."""

    def __init__(self):
        """Create BME280 device and initialise temperature metric gauge."""
        from odin_devices.bme280 import BME280

        self.device = BME280(use_spi=False, bus=2)
        self.temp_gauge = Gauge('temp_bme280', 'Temperature reading on BME280')

    def read_temp(self):
        """Read current temperature."""
        data = self.device.temperature
        self.temp_gauge.set(data)


class BME280TemperatureCollector:
    """Class to collect temperature reading from BME280 devices."""

    def __init__(self, options):
        """Creates BMEReader object."""
        self.bme = BME280Reader()

    def collect_metrics(self):
        """Collects temperature reading."""
        self.bme.read_temp()


class DS18B20TemperatureCollector:
    """Class to create DS18B20 devices and collect temperature reading."""

    def __init__(self, options):
        """Checks connected devices and assigns nicknames from config."""
        from pathlib import Path

        self.ds18b20_devices = []
        self.ds18b20_device_paths = list(Path('/sys/bus/w1/devices').glob('28-*'))

        try:
            self.names = options["names"]

            for i in range(len(self.ds18b20_device_paths)):
                path = self.ds18b20_device_paths[i]
                name = self.names[i]
                ds18b20_device = DS18B20Reader(path, name)
                self.ds18b20_devices.append(ds18b20_device)

        except TypeError:
            print(f"{self} ERROR - collector needs \"names\" option")

        except IndexError:
            print(f"{self} ERROR - there must be names for each device")

    def collect_metrics(self):
        """Collects temperature reading from each device."""
        for device in self.ds18b20_devices:
            device.read_temp()
