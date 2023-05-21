from plugins.qbittorrent_service_monitor import QBittorrentMonitor
from plugins.plex_service_monitor import PlexMonitor
from plugins.process_monitor import ProcessMonitor
from time import sleep
from os import system
import sys

MONITORING_PERIOD = 30 #30 min

def load_monitors():
    monitors = [
        QBittorrentMonitor(),
        PlexMonitor(),
        ProcessMonitor()
    ]
    return monitors

def init_config_path(monitors, config_folder):
    for monitor in monitors:
        monitor.set_config_path(config_folder)

def any_monitor_has_activity(monitors):
    any_activity = False
    for monitor in monitors:
        if monitor.is_enabled() and monitor.has_activity():
            print("Service: %s has active" % monitor.service_name())
            any_activity = True
    return any_activity

def check_monitor_activity(monitors):
    current_iteration = 0
    while True:
        status = any_monitor_has_activity(monitors)
        if status:
            current_iteration = 0
        else:
            current_iteration += 1
        print("Iteration count: %d" % current_iteration)
        if current_iteration == MONITORING_PERIOD:
            break
        sleep(60)

def shutdown_pc():
    system("systemctl poweroff")

if __name__ == "__main__":
    print("Starting monitoring")
    if len(sys.argv) != 2:
        print("python monitor.py <config_dir>")
        exit(1)
    config = sys.argv[1]
    print("Config folder: %s" % config)
    monitors = load_monitors()
    if len(monitors) == 0:
        print("No monitor configured")
        exit(1)
    init_config_path(monitors=monitors, config_folder=config)
    check_monitor_activity(monitors)
    shutdown_pc()