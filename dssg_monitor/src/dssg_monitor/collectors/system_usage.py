from prometheus_client import Gauge

class SystemUsageCollector:
    """
    Class to manage the creation and updating of Prometheus Gauges related to system usage metrics.
    """

    def __init__(self, options):
        """
        Initialise system usage metric gauges.
        
        - Defines Prometheus Gauge's for metrics.
        - Registers all defined gauges in the Prometheus global registry automatically.
        """
        # Lazy imports, only use imports where directly needed
        import os 
        import socket

        self.machine_name = (os.getenv("MACHINE_NAME", socket.gethostname())).split(".")[0]

        # Define Prometheus gauges in the global prometheus registry, to be picked up by the exporter server.
        self.cpu_usage = Gauge("cpu_usage", "CPU usage percentage", ["machine"])
        self.memory_usage = Gauge("memory_usage", "Memory usage percentage, including buffer/cache", ["machine"])
        self.disk_usage = Gauge("disk_usage", "Disk space usage percentage", ["machine"])
        self.terminal_count = Gauge("terminal_count", "Number of open terminals", ["machine"])
        self.user_count = Gauge("user_count", "Number of users connected", ["machine"])
        self.load_1m = Gauge("load_1m", "System load average over 1 minute", ["machine"])
        self.cpu_temp = Gauge("cpu_temp", "CPU temperature in Celsius", ["machine"])

    def get_terminal_count(self):
        """
        Count active terminal (PTS) sessions.
        
        :return: int - Number of open terminal sessions.
        """
        import subprocess
        try:
            output = subprocess.check_output("ls /dev/pts/ | wc -l", shell=True, text=True).strip()
            return int(output)
        except Exception:
            return 0
        
    def get_unique_users(self):
        """
        Count unique users running a shell session (bash/zsh/sh).
        
        :return: int - Number of unique users.
        """
        import subprocess
        try:
            output = subprocess.check_output(
                "ps -eo user,comm | grep -E 'bash|zsh|sh' | awk '{print $1}' | sort -u | wc -l",
                shell=True, text=True).strip()
            return int(output)
        except Exception:
            return 0

    def get_cpu_temperature(self):
        """
        Retrieve CPU temperature in Celsius.
        
        :return: float - CPU temperature in degrees Celsius, or 0 if unavailable.
        """
        import psutil
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                return temps["coretemp"][0].current
            elif "cpu-thermal" in temps:
                return temps["cpu-thermal"][0].current
            elif "acpitz" in temps:
                return temps["acpitz"][0].current
            return 0
        except Exception:
            return 0
        
    def collect_metrics(self):
        """
        Update system metrics gauges with the latest values.
        
        - Retrieves system usage statistics and updates the corresponding Prometheus gauges.
        - The updated values are automatically available to Prometheus when it scrapes the `/metrics` endpoint.
        """
        import psutil
        self.cpu_usage.labels(machine=self.machine_name).set(psutil.cpu_percent(interval=None))
        self.memory_usage.labels(machine=self.machine_name).set(psutil.virtual_memory().percent)
        self.disk_usage.labels(machine=self.machine_name).set(psutil.disk_usage('/').percent)
        self.terminal_count.labels(machine=self.machine_name).set(self.get_terminal_count())
        self.user_count.labels(machine=self.machine_name).set(self.get_unique_users())
        self.load_1m.labels(machine=self.machine_name).set(psutil.getloadavg()[0])
        self.cpu_temp.labels(machine=self.machine_name).set(self.get_cpu_temperature())