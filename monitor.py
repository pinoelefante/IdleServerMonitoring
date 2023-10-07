from libs.service_monitor_base import ServiceMonitorBase
from libs.shutdown_service import ShutdownService
from time import sleep
import sys
import os
import importlib
import signal
import json

class MonitoringService:

    def __init__(self, config_path:str, plugin_path:str) -> None:
        self.shutdown_service = ShutdownService()
        if not self.shutdown_service.can_shutdown():
            print("User can't shutdown the server")
            exit(-1)
        self.config_path = config_path
        self.plugin_path = plugin_path

    def start(self):
        print("Starting monitoring service")
        self.do_reload = False
        self.load_system_config()
        self.load_monitors(self.config_path, self.plugin_path)
        if len(self.monitors) == 0:
            print("No monitor configured")
            exit(1)
        self.check_monitor_activity()

    def load_system_config(self):
        config_file_path = os.path.join(self.config_path, "system.json")
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as f:
                config_data=json.load(f)
            self.monitoring_period = int(config_data.get("window_time_in_minutes", "30"))
            self.check_interval = int(config_data.get("check_activity_period_in_seconds", "30"))
        else:
            self.monitoring_period = 30
            self.check_interval = 30
        print("Monitoring period: %d minutes" % self.monitoring_period)
        print("Check interval: %s seconds" % self.check_interval)

    def reload(self):
        self.stop_monitors()
        self.start()

    def stop_monitors(self):
        for m in self.monitors:
            m.stop()

    def request_reload(self):
        print("Reloading monitoring service...Wait for next interval check")
        self.do_reload = True

    def load_monitors(self, config_path, plugin_path) -> list[ServiceMonitorBase]:
        modules = []
        files = filter(lambda filename : filename.find(".py") > 0, os.listdir(plugin_path))
        for f in files:
            module = importlib.import_module("plugins.%s" % f.split(".")[0])
            instance = module.Plugin(config_path=config_path)
            modules.append(instance)
        self.monitors = modules

    def any_monitor_has_activity(self, monitors) -> bool:
        any_activity = False
        for monitor in monitors:
            if not monitor.is_enabled():
                continue
            try:
                if monitor.has_activity():
                    print("Detected activity for service %s" % monitor.service_name())
                    any_activity = True
            except:
                print("Error while checking activity with plugin %s" % monitor.service_name())
        return any_activity

    def check_monitor_activity(self):
        current_iteration = 0
        monitoring_iterations = int((self.monitoring_period * 60) / self.check_interval)
        if monitoring_iterations < 1:
            monitoring_iterations = 1
        while current_iteration < monitoring_iterations:
            try:
                sleep(self.check_interval)
            except:
                print("Sleep interrupted")
                break
            if self.do_reload:
                break
            print("Checking activity...")
            current_iteration += 1
            if current_iteration > 0 and current_iteration % 10 == 0:
                print("Iteration count: %d" % current_iteration)
            if self.any_monitor_has_activity(self.monitors):
                current_iteration = 0
        
        if self.do_reload:
            self.reload()
        else:
            self.shutdown_pc()

    def shutdown_pc(self):
        print("Shutting down")
        self.shutdown_service.shutdown()

    def signal_handler(self, signal, frame):
        self.request_reload()

if __name__ == "__main__":
    print("Loading monitoring service")
    cwd_path = os.path.dirname(sys.argv[0])
    
    config_path = os.path.join(cwd_path, "configs")
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    print("Config folder: %s" % config_path)
    if not os.path.isdir(config_path):
        print("You must provide a valid directory for configs")
        exit(1)
    
    plugin_path=os.path.join(cwd_path, "plugins")
    print("Plugin folder: %s" % plugin_path)

    monitoring = MonitoringService(config_path, plugin_path)
    
    signal.signal(signal.SIGHUP, monitoring.signal_handler)
    monitoring.start()