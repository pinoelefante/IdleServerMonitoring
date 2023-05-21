from libs.service_monitor_base import ServiceMonitorList
from plugins.qbittorrent_service_monitor import QBittorrentMonitor
from plugins.plex_service_monitor import PlexMonitor
from plugins.process_monitor import ProcessMonitor
from plugins.ssh_user_monitor import SSHConnectedUserMonitor
from time import sleep
from os import system
import sys

MONITORING_PERIOD = 30 #30 min

class MonitoringService:

    def start(self, config):
        monitors = self.load_monitors()
        if len(monitors) == 0:
            print("No monitor configured")
            exit(1)
        self.init_config_path(monitors=monitors, config_folder=config)
        self.check_monitor_activity(monitors)
        self.shutdown_pc()

    def load_monitors(self) -> ServiceMonitorList:
        monitors = [
            QBittorrentMonitor(),
            PlexMonitor(),
            ProcessMonitor(),
            SSHConnectedUserMonitor()
        ]
        return monitors

    def init_config_path(self, monitors:ServiceMonitorList, config_folder:str):
        for monitor in monitors:
            monitor.set_config_path(config_folder)

    def any_monitor_has_activity(self, monitors:ServiceMonitorList) -> bool:
        any_activity = False
        for monitor in monitors:
            if monitor.is_enabled() and monitor.has_activity():
                print("Detected activity for service %s" % monitor.service_name())
                any_activity = True
        return any_activity

    def check_monitor_activity(self, monitors:ServiceMonitorList):
        current_iteration = 0
        while True:
            status = self.any_monitor_has_activity(monitors)
            if status:
                current_iteration = 0
            else:
                current_iteration += 1
            print("Iteration count: %d" % current_iteration)
            if current_iteration == MONITORING_PERIOD:
                break
            sleep(60)

    def shutdown_pc(self):
        #https://tojaj.com/how-to-turn-off-a-linux-system-without-root-or-sudo/
        system("systemctl poweroff")

if __name__ == "__main__":
    print("Starting monitoring")
    if len(sys.argv) != 2:
        print("python monitor.py <config_dir>")
        exit(1)
    config = sys.argv[1]
    print("Config folder: %s" % config)

    monitoring = MonitoringService()
    monitoring.start(config)