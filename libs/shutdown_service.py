from os import system
from libs.utils import is_linux, is_windows
if is_linux():
    import dbus

class ShutdownBase:
    def can_shutdown(self) -> bool:
        return True

    def shutdown(self):
        pass

    def hibernate(self):
        pass

    def restart(self):
        pass

    def interrupt(self):
        pass

class ShutdownService(ShutdownBase):
    def __init__(self) -> None:
        if is_linux():
            self.service = LinuxShutdown()
        elif is_windows():
            self.service = WindowsShutdown()
    
    def can_shutdown(self) -> bool:
        return self.service.can_shutdown()

    def shutdown(self):
        return self.service.shutdown()

    def hibernate(self):
        return self.service.hibernate()

    def restart(self):
        return self.service.restart()

    def interrupt(self):
        return self.service.interrupt()

class WindowsShutdown(ShutdownBase):
    def shutdown(self):
        system("shutdown /s /f /t 0")

    def hibernate(self):
        system("shutdown /h /t 0")

    def restart(self):
        system("shutdown /r /f /t 0")

    def interrupt(self):
        system("shutdown /a /f /t 0")

class LinuxShutdown(ShutdownBase):
    #https://tojaj.com/how-to-turn-off-a-linux-system-without-root-or-sudo/

    def __init__(self) -> None:
        sys_bus = dbus.SystemBus()
        ck_srv = sys_bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
        self.ck_iface = dbus.Interface(ck_srv, 'org.freedesktop.login1.Manager')

    def can_shutdown(self) -> bool:
        can =  self.ck_iface.get_dbus_method("CanPowerOff")()
        return can
    
    def shutdown(self):
        try:
            self.ck_iface.get_dbus_method("PowerOff")(False)
        except dbus.exceptions.DBusException:
            print("Make sure you can shutdown the computer without being root")
            print("""
Prepare PolicyKit permissions:
As root create a new policy file:
/etc/polkit-1/localauthority/50-local.d/allow_all_users_to_shutdown.pkla

and add the following content:

[Allow all users to shutdown]
Identity=unix-user:*
Action=org.freedesktop.login1.power-off;org.freedesktop.login1.power-off-multiple-sessions
ResultActive=yes
ResultAny=yes

Save the file and reload daemon
systemctl daemon-reload

Credits: https://tojaj.com/how-to-turn-off-a-linux-system-without-root-or-sudo/
""")