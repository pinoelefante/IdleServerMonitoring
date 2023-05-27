from os.path import join, exists
from json import load

class ServiceMonitorBase:

    def __init__(self, config_path) -> None:
        self.set_config_path(config_path)

    def __del__(self):
        self.stop()

    def is_enabled(self) -> bool:
        current_conf = self.config_data.get("enabled", "true")
        return current_conf == "true"
    
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

