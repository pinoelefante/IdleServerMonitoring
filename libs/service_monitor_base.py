from os.path import join, exists
from json import load
import sys

class ServiceMonitorBase:

    def __del__(self):
        self.stop()

    def is_enabled(self) -> bool:
        has_attr = hasattr(self.config_data, "enabled")
        return not has_attr or (has_attr and bool(self.config_data.get("enabled", True)))
    
    def has_activity(self) -> bool:
        return False
    
    def reload(self):
        self.stop()
        print("Reloading %s" % self.service_name())
        if exists(self.config_file_path()):
            with open(self.config_file_path(), "r") as f:
                self.config_data=load(f)
        else:
            self.config_data=dict()
        self.after_config_file_loaded()

    def after_config_file_loaded(self):
        pass

    def stop(self):
        print("Stopping %s" % self.service_name())

    def config_file_path(self) -> str:
        config_path = self.config_path if hasattr(self, "config_path") else "."
        return join(config_path, self.config_filename())

    def config_filename(self) -> str:
        return "%s.json" % self.service_name()
    
    def service_name(self) -> str:
        return self.__class__.__name__

    def set_config_path(self, config_folder:str):
        self.config_path=config_folder
        self.reload()

    def is_linux(self) -> bool:
        return sys.platform.startswith("linux")

    def is_windows(self) -> bool:
        return sys.platform.startswith("win")
    
    def is_mac(self) -> bool:
        return sys.platform.startswith("darwin")
