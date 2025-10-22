import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(__file__))

from service import ZKTecoService

class ZKTecoWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ZKTecoAttendanceService"
    _svc_display_name_ = "Service Pointage ZKTeco"
    _svc_description_ = "Service de synchronisation automatique des pointages ZKTeco vers l'API"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.service = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.service:
            self.service.stop()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        self.service = ZKTecoService()
        self.service.start()
        
        # Attendre l'arrêt
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ZKTecoWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ZKTecoWindowsService)