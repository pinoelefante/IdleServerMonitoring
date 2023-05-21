from libs.service_monitor_base import ServiceMonitorBase
import psutil

class DiskActivityMonitor(ServiceMonitorBase):

    def has_activity(self) -> bool:
        stats = psutil.disk_io_counters(perdisk=False)
        written_treshold = self.config_data.get("data_written_between_interval_in_mb", 64)
        read_treshold = self.config_data.get("data_read_between_interval_in_mb", 32)
        written = self.get_data_in_mb(stats.write_bytes)
        read = self.get_data_in_mb(stats.read_bytes)
        if not hasattr(self, "past_written") or not hasattr(self, "past_read"):
            self.save_data(written, read)
            return True
        past_read = self.past_read
        past_written = self.past_written
        self.save_data(written, read)
        return read-past_read > read_treshold or written-past_written > written_treshold
    
    def get_data_in_mb(self, stats):
        return stats / 1048576
    
    def save_data(self, written, read):
        self.past_written = written
        self.past_read = read