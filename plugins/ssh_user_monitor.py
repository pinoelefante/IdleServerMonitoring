from libs.service_monitor_base import ServiceMonitorBase
from libs.utils import is_linux
from subprocess import PIPE, Popen

class SSHConnectedUserMonitor(ServiceMonitorBase):
    def has_activity(self):
        user_command = self.config_data.get("user_list_command", "who")
        grep_string = self.config_data.get("grep_string", "pts")
        count_cmd = self.config_data.get("count_command", "wc -l")
        command = "%s | grep '%s' | %s" % (user_command, grep_string, count_cmd)
        connected_users = int(self.run_shell_command(command))
        print("Connected users ssh: %d" % connected_users)
        return connected_users > 0
    
    def is_enabled(self):
        return is_linux() and super().is_enabled()
    
    def run_shell_command(self, command):
        process = Popen(args=command, stdout=PIPE, shell=True)
        return process.communicate()[0]