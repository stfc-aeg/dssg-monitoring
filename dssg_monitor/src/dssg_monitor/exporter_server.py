import logging
import time
import yaml

from prometheus_client import start_http_server
from .collectors.system_usage import SystemUsageCollector
from .collectors.temperature import BME280TemperatureCollector, DS18B20TemperatureCollector

#Create a dssg-monitor logger, and asign its logging level to debug
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - dssg-monitor - %(levelname)s - %(message)s",
    datefmt="%d-%m-%y %H:%M:%S")

class MetricExporter:
    """
    Class to handle the instantiation of metric collectors and then export the metrics 
    using a Prometheus HTTP server.

    :param config_path: str - Path to the configuration YAML file.
    """

    def __init__(self, config_path):
        """
        Initialise the MetricExporter class.
        
        :param config_path: str - Path to the configuration YAML file.

        - Reads in the configuration file.
        - Extracts server parameters (IP address and port).
        - Loads the list of metric collectors to initialise.
        - Initialises supported metric collectors.
        """
        self.config = self.load_config(config_path)
        self.host_ip = self.config["server_ip"]
        self.host_port = self.config["server_port"]
        self.collector_list = self.config["collectors"]
        self.instantiated_collectors = []

         # Define supported metric collectors, map collector names to classes
        self.supported_collectors = {
            "system_usage": SystemUsageCollector(), 
            "bme280_temperature": BME280TemperatureCollector(),
            "ds18b20_temperature": DS18B20TemperatureCollector(self.config["ds18b20_names"]) 
        }

        # Initialise each collector specified in the config
        for collector in self.collector_list:
            if collector in self.supported_collectors:
                self.instantiated_collectors.append(self.supported_collectors[collector])
                logging.info(f"Instantiated collector: {collector}")
            else:
                logging.error(f"Collector: {collector} not recognised")
        # Start the Prometheus HTTP server and metric collection loop
        self.start()

    def load_config(self, config_path):
        """
        Load the configuration from a YAML file.
        
        :param config_path: str - Path to the configuration YAML file.
        :return: dict - Parsed configuration data.
        
        If the file cannot be found or read, logs an error and exits the program.
        """
        try:
            with open(config_path) as stream:
                conf = yaml.safe_load(stream)       
        except Exception as e:
            logging.error("File not found, exiting")
            exit()
        return conf
    
    def start(self):
        """
        Start the Prometheus HTTP server and periodically collect metrics.
        
        - Calls `start_http_server()` from the `prometheus_client` package to expose metrics.
        - `start_http_server` automatically retrieves metric gauges registered in the global Prometheus registry.
        - The HTTP server exposes the `/metrics` endpoint
        - Calls `collect_metrics()` on each instantiated collector to refresh metric values.
        
        The Prometheus server, when configured to scrape this exporter, will query the `/metrics`
        endpoint and retrieve the latest values of the metrics.
        """
        start_http_server(port=int(self.host_port), addr=self.host_ip)
        logging.info(f"Prometheus metrics exposed at http://{self.host_ip}:{self.host_port}/metrics")

        while True:
            for collector in self.instantiated_collectors:
                try:
                    collector.collect_metrics()
                except Exception as e:
                    logging.error(f"Could not collect metrics for {collector}, Encountered: {e}")
            time.sleep(1)