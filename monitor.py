from libs.service_monitor_base import ServiceMonitorBase
from libs.shutdown_service import ShutdownService
from time import sleep
import sys
import os
import importlib

MONITORING_PERIOD = 1 #30 min
CHECK_INTERVAL_IN_SECS = 30
MONITORING_ITERATIONS = (MONITORING_PERIOD * 60) / CHECK_INTERVAL_IN_SECS

class MonitoringService:

    def __init__(self) -> None:
        self.shutdown_service = ShutdownService()
        if not self.shutdown_service.can_shutdown():
            print("User can't shutdown the server")
            exit(-1)

    def start(self, config):
        self.load_monitors(config)
        if len(self.monitors) == 0:
            print("No monitor configured")
            exit(1)
        self.check_monitor_activity()
        self.shutdown_pc()

    def load_monitors(self, config_path) -> list[ServiceMonitorBase]:
        modules = []
        files = filter(lambda filename : filename.find(".py") > 0, os.listdir("plugins")) 
        for f in files:
            module = importlib.import_module("plugins.%s" % f.split(".")[0])
            instance = module.Plugin(config_path=config_path)
            modules.append(instance)
        self.monitors = modules

    def init_config_path(self, config_folder:str):
        for monitor in self.monitors:
            monitor.set_config_path(config_folder)

    def any_monitor_has_activity(self) -> bool:
        any_activity = False
        monitors = self.monitors
        for monitor in monitors:
            if not monitor.is_enabled():
                continue
            if monitor.has_activity():
                print("Detected activity for service %s" % monitor.service_name())
                any_activity = True
        return any_activity

    def check_monitor_activity(self):
        current_iteration = 0
        while True:
            status = self.any_monitor_has_activity(self.monitors)
            if status:
                current_iteration = 0
            else:
                current_iteration += 1
            if current_iteration > 0 and current_iteration % 10 == 0:
                print("Iteration count: %d" % current_iteration)
            if current_iteration == MONITORING_ITERATIONS:
                break
            sleep(CHECK_INTERVAL_IN_SECS)

    def shutdown_pc(self):
        self.shutdown_service.shutdown()

if __name__ == "__main__":
    print("Starting monitoring")
    if len(sys.argv) != 2:
        print("python monitor.py <config_dir>")
        exit(1)
    config = sys.argv[1]
    if not os.path.isdir(config):
        print("You must provide a valid directory for configs")
        exit(1)
    print("Config folder: %s" % config)
    monitoring = MonitoringService()
    monitoring.start(config)