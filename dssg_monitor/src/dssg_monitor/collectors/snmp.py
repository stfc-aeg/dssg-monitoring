from prometheus_client import Gauge
from puresnmp import Client, V2C, PyWrapper
import asyncio
import time

class SnmpReader:
    """Class to manage the SNMP connection for a given address, and make specified requests."""

    def __init__(self, name, address, requests):
        """Initialise the snmp client and gauges for each value."""
        self.name = name
        self.address = address
        self.readings = {}
        self.requests = requests
        # SNMP client
        self.client = PyWrapper(Client(self.address, V2C("public")))

        # Each value gets a Gauge to be written to
        for val in self.requests.keys():
            # Descriptions are unfortunately generic
            label = f"{name}_{val}"
            desc = f"Reading of the {val} for the {name} PDU rack."
            # Each value has a reading and a Gauge, so the Gauge can be set separately to receiving the value
            self.readings[val] = {}
            self.readings[val]['reading'] = 0
            self.readings[val]['gauge'] = Gauge(label, desc)

        # Time tracking
        self.last_update = 0
        self.update_interval = 1

    async def update_readings(self):
        """Poll SNMP OIds and update readings asynchronously."""
        for val, req in self.requests.items():
            out = await self.client.get(req)
            self.readings[val]['reading'] = out
        await asyncio.sleep(1)

    def check_update(self):
        """Time-checker function to manage asynchronous tasks."""
        now = time.time()
        if now - self.last_update >= self.update_interval:
            asyncio.run(self.update_readings())
            self.last_update = now

class SnmpCollector:
    """Class to create the SNMP reader and collect the values."""

    def __init__(self, options):
        """Gather and format snmp request details for the class."""
        import logging

        self.readers = {}

        try:
            # See snmp.yaml
            for name in options.keys():
                address = options[name]['address']
                requests = options[name]['requests']
                self.readers[name] = SnmpReader(name, address, requests)
        except Exception as e:
            logging.debug(f"Error: {e}")

    def collect_metrics(self):
        """Collect the current values and set the Gauge."""
        for reader in self.readers.values():
            reader.check_update()  # Update values if needed
            # Set gauge to the latest reading, whenever it has come in
            for name, values in reader.readings.items():
                values['gauge'].set(values['reading'])
