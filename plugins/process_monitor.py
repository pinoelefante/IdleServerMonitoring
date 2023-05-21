import psutil
from libs.service_monitor_base import ServiceMonitorBase

class ProcessMonitor(ServiceMonitorBase):
    
    def has_activity(self):
        processes = self.config_data
        for process_name in processes:
            if self.is_process_active(process_name):
                return True
        return False
    
    def is_process_active(self, process_name):
        for proc in psutil.process_iter():
            try:
                if process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False