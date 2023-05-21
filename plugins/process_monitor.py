import psutil
from libs.service_monitor_base import ServiceMonitorBase

class ProcessMonitor(ServiceMonitorBase):
    
    def has_activity(self):
        processes = self.config_data
        if len(processes) == 0:
            return False
        running_processes = psutil.process_iter()
        for process_name in processes:
            if self.is_process_active(process_name, running_processes):
                return True
        return False
    
    def is_process_active(self, process_name, running_processes):
        for proc in running_processes:
            try:
                if process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False