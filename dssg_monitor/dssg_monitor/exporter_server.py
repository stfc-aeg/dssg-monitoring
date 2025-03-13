import logging

# import psutil
# import subprocess
# from prometheus_client import Gauge
# import socket
# import os
import yaml

#Create a dssg-monitor logger, and asign its logging level to debug
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - dssg-monitor - %(levelname)s - %(message)s",
    datefmt="%d-%m-%y %H:%M:%S"
)

class MetricExporter:
    """Class to handle the instantiation of metric collectors and then export the metric using a 
    prometheus http server"""

    def __init__(self, config_path):
        """"Read in config file, obtain server parameters and metric collectors to initialise"""
        self.config = self.load_config(config_path)
        self.host_ip = self.config["server_ip"]
        self.host_port = self.config["server_port"]
        self.collector_list = self.config["collectors"]

        logging.info(f"Obtained config for dssg-monitor of {self.host_ip}:{self.host_port} with modules : {self.collector_list} ")

    def load_config(self, config_path):
        """Open config file as stream, """
        try:
            with open(config_path) as stream:
                conf = yaml.safe_load(stream)       
        except Exception as e:
            logging.error("File not found, exiting")
            exit()
        return conf