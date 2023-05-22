from libs.service_monitor_base import ServiceMonitorBase
from libs.shutdown_service import ShutdownService
from plugins.qbittorrent_service_monitor import QBittorrentMonitor
from plugins.plex_service_monitor import PlexMonitor
from plugins.process_monitor import ProcessMonitor
from plugins.ssh_user_monitor import SSHConnectedUserMonitor
from plugins.disk_activity_monitor import DiskActivityMonitor
from time import sleep
import sys


MONITORING_PERIOD = 1 #30 min
CHECK_INTERVAL_IN_SECS = 30
MONITORING_ITERATIONS = (MONITORING_PERIOD * 60) / CHECK_INTERVAL_IN_SECS

class MonitoringService:

    def __init__(self) -> None:
        self.shutdown_service = ShutdownService()

    def start(self, config):
        monitors = self.load_monitors()
        if len(monitors) == 0:
            print("No monitor configured")
            exit(1)
        self.init_config_path(monitors=monitors, config_folder=config)
        self.check_monitor_activity(monitors)
        self.shutdown_pc()

    def load_monitors(self) -> list[ServiceMonitorBase]:
        monitors = [
            QBittorrentMonitor(),
            PlexMonitor(),
            #ProcessMonitor(),
            #SSHConnectedUserMonitor(),
            #DiskActivityMonitor()
        ]
        return monitors

    def init_config_path(self, monitors:list[ServiceMonitorBase], config_folder:str):
        for monitor in monitors:
            monitor.set_config_path(config_folder)

    def any_monitor_has_activity(self, monitors:list[ServiceMonitorBase]) -> bool:
        any_activity = False
        for monitor in monitors:
            if monitor.is_enabled() and monitor.has_activity():
                print("Detected activity for service %s" % monitor.service_name())
                any_activity = True
        return any_activity

    def check_monitor_activity(self, monitors:list[ServiceMonitorBase]):
        current_iteration = 0
        while True:
            status = self.any_monitor_has_activity(monitors)
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
        sleep(2)
        self.shutdown_service.interrupt()

if __name__ == "__main__":
    print("Starting monitoring")
    if len(sys.argv) != 2:
        print("python monitor.py <config_dir>")
        exit(1)
    config = sys.argv[1]
    print("Config folder: %s" % config)

    monitoring = MonitoringService()
    monitoring.start(config)