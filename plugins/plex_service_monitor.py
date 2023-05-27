from libs.service_monitor_base import ServiceMonitorBase
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount

class Plugin(ServiceMonitorBase):
    def has_activity(self):
        if self.plexserver == None:
            return False
        try:
            sessions = self.plexserver.sessions()
            return len(sessions) > 0
        except:
            print("Plex: can't list running sessions")
            return False
    
    def after_config_file_loaded(self):
        try:
            if "baseurl" in self.config_data and "token" in self.config_data:
                self.access_using_token(**self.config_data)
            else:
                self.access_using_myplex(**self.config_data)
        except:
            print("Can't access Plex Server")
            self.plexserver = None
    
    def stop(self):
        super().stop()
        self.plexserver = None

    def access_using_token(self, baseurl, token):
        print("Plex: access using token")
        self.plexserver = PlexServer(baseurl=baseurl, token=token)

    def access_using_myplex(self, username, password, server_name):
        print("Plex: access using MyPlex")
        account = MyPlexAccount(username=username, password=password)
        self.plexserver = account.resource(server_name).connect()
    
    def service_name(self) -> str:
        return "PlexMonitor"