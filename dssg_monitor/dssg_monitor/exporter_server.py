import logging
import time
import yaml

from prometheus_client import start_http_server
from .collectors.system_usage import SystemUsageCollector

#Create a dssg-monitor logger, and asign its logging level to debug
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - dssg-monitor - %(levelname)s - %(message)s",
    datefmt="%d-%m-%y %H:%M:%S")

class MetricExporter:
    """Class to handle the instantiation of metric collectors and then export the metric using a 
    prometheus http server"""

    def __init__(self, config_path):
        """"Read in config file, obtain server parameters and metric collectors to initialise"""
        self.config = self.load_config(config_path)
        self.host_ip = self.config["server_ip"]
        self.host_port = self.config["server_port"]
        self.collector_list = self.config["collectors"]
        self.instantiated_collectors = []

        self.supported_collectors = {
            "system_usage": SystemUsageCollector
        }

        for collector in self.collector_list:
            if collector in self.supported_collectors:
                self.instantiated_collectors.append(self.supported_collectors[collector]())
                logging.info(f"Instantiated collector: {collector}")
            else:
                logging.error(f"Collector: {collector} not recognised")
        self.start()

    def load_config(self, config_path):
        """Open config file as stream, """
        try:
            with open(config_path) as stream:
                conf = yaml.safe_load(stream)       
        except Exception as e:
            logging.error("File not found, exiting")
            exit()
        return conf
    
    def start(self):
        start_http_server(port=int(self.host_port), addr=self.host_ip)
        logging.info(f"Prometheus metrics exposed at http://{self.host_ip}:{self.host_port}/metrics")

        while True:
            for collector in self.instantiated_collectors:
                collector.collect_metrics()
            time.sleep(1)