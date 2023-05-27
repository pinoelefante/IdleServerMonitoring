from typing import Iterator
import psutil
from libs.service_monitor_base import ServiceMonitorBase

class Plugin(ServiceMonitorBase):
    
    def has_activity(self):
        processes = self.config_data["processes"]
        if len(processes) == 0:
            return False
        running_processes = list(psutil.process_iter(["pid", "name", "username"]))
        for process_name in processes:
            if self.is_process_active(process_name, running_processes):
                return True
        return False
    
    def is_process_active(self, process_name:str, running_processes:Iterator[psutil.Process]):
        process_search = process_name.lower().strip()
        for proc in running_processes:
            proc_name = proc.name().lower().strip()
            try:
                if proc_name == process_name.lower() or proc_name.startswith(process_search):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    
    def service_name(self) -> str:
        return "ProcessMonitor"