# dssg-monitoring
Monitoring of the labs for Sustainability


# DSSG-Monitor

Package managed with pyproject.toml to allow for the collection of metrics from different "collector" modules, and export them using a prometheusclient http_server

Installed with pip install .[{collector_name}, {collector_2_name}]

Requires Python 3.10 >=

# Running dssg-monitor

## Installing

Clone the repo, create a virtualenv, pip install .[collector_name]

The 'collector_name' comes from the pyproject.toml optional dependency list, which will install only the dependencies required for that specific collector

```bash
pip install .[system_usage]
Processing /aeg_sw/work/users/cfq49458/develop/dssg-monitoring/dssg_monitor
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Requirement already satisfied: pyyaml in /aeg_sw/work/users/cfq49458/develop/dssg/lib/python3.8/site-packages (from dssg-monitor==0.0.0) (6.0.3)
Requirement already satisfied: prometheus-client in /aeg_sw/work/users/cfq49458/develop/dssg/lib/python3.8/site-packages (from dssg-monitor==0.0.0) (0.21.1)
Requirement already satisfied: psutil in /aeg_sw/work/users/cfq49458/develop/dssg/lib/python3.8/site-packages (from dssg-monitor==0.0.0) (7.1.0)
Building wheels for collected packages: dssg-monitor
  Building wheel for dssg-monitor (pyproject.toml) ... done
  Created wheel for dssg-monitor: filename=dssg_monitor-0.0.0-py3-none-any.whl size=7311 sha256=8188e771659f867ff51d265a7024e47b1d4f06c90e1848ae4ef402a84c5b1ad7
  Stored in directory: /tmp/pip-ephem-wheel-cache-b45e17bw/wheels/4b/53/39/ecfaea091b60143bd418212a632f43ca75fbebe233e3438468
Successfully built dssg-monitor
Installing collected packages: dssg-monitor
  Attempting uninstall: dssg-monitor
    Found existing installation: dssg-monitor 0.0.0
    Uninstalling dssg-monitor-0.0.0:
      Successfully uninstalled dssg-monitor-0.0.0
Successfully installed dssg-monitor-0.0.0
```

## Config File

Create a CONFIG_NAME.yaml file in the /configs directory with the following structure:


server_ip: 'xxx.xxx.xxx.xxx'
server_port: xxxx
collectors:
  'PATH_TO_COLLECTOR.COLLECTOR_NAME':
    OPTION_KEY: OPTION_VALUE
  'dssg_monitor.collectors.temperature.DS18B20TemperatureCollector':
    names: ["aircon"]


## Launching collector

When a suitable config is created and the package is installed as above

```bash
dssg-monitor --config src/dssg_monitor/configs/system_usage.yaml 
10-10-25 13:30:44 - dssg-monitor - INFO - Instantiated collector: dssg_monitor.collectors.system_usage.SystemUsageCollector
10-10-25 13:30:44 - dssg-monitor - INFO - Prometheus metrics exposed at http://192.168.0.XX:8866/metrics
```

## Importing Metrics

When the metrics are being exposed on an address

The metric endpoint target can be added to the docker/prometheus/prometheus.yml in the scrape configs section

At the time of writing there are a few sections relating to different collectors
dev-machines - system_usage collector
temp sensors - temperature collector
rack pdu - snpm collector

When a new metric endpoint is being exposed, add the target of this new metric to the relevant target list for that collector. For example, when adding a new metric endpoint that is exposing a system_usage collector
```yaml
  - job_name: "dev-machines"
    scrape_interval: 5s
    static_configs:
      - targets:
          - "192.168.0.XX:8866"
```