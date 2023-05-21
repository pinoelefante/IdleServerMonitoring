import qbittorrentapi
from libs.service_monitor_base import ServiceMonitorBase

RATIO_KEY = "ratio"
LAST_ACTIVITY_KEY = "last_activity"
PROGRESS_KEY = "progress"
HASH_KEY = "hash"

class QBittorrentMonitor(ServiceMonitorBase):
    def reload(self):
        super().reload()
        self.monitor_data = dict() ## clear and init monitor data

    def after_config_file_loaded(self):
        self.client = qbittorrentapi.Client(**self.config_data)
        try:
            self.client.auth_log_in()
        except qbittorrentapi.LoginFailed as e:
            print(e)

    def stop(self):
        super().stop()
        if hasattr(self, "client") and self.client != None:
            self.client.auth_log_out()

    def has_activity(self):
        try:
            downloading = self.client.torrents.info.downloading()
        except:
            print("Error while fetching downloading torrent")
            return False

        if len(downloading) == 0:
            self.monitor_data.clear()
            return False
        any_active=False
        for d in downloading:
            if self.download_torrent_has_activity(d):
                any_active = True
        return any_active
    
    def download_torrent_has_activity(self, torrent):
        t_hash = torrent[HASH_KEY]
        t_progress = torrent[PROGRESS_KEY] #download percentage

        if self.monitor_data.get(t_hash, None) == None:
            self.set_monitor_torrent(torrent)
            return True

        past_data = self.monitor_data.get(t_hash)
        past_progress = past_data[PROGRESS_KEY]
        self.set_monitor_torrent(torrent)
        return t_progress != past_progress

    def set_monitor_torrent(self, torrent):
        t_hash = torrent[HASH_KEY]
        t_last_activity = torrent[LAST_ACTIVITY_KEY]
        t_progress = torrent[PROGRESS_KEY] #download percentage
        t_ratio = torrent[RATIO_KEY] #share ratio
        self.monitor_data.update( {t_hash: { LAST_ACTIVITY_KEY: t_last_activity, PROGRESS_KEY: t_progress, RATIO_KEY: t_ratio} })