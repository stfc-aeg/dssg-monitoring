import argparse

from .exporter_server import MetricExporter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    args = parser.parse_args()
    config_path = args.config

    exporter = MetricExporter(config_path)
