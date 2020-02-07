from pushbullet.pushbullet import PushBullet
from modules.conf import read_conf

class Alerteur():
    """classe de pilotage des alertes"""
    def __init__(self):
        cfg = read_conf("global")
        self.pb = PushBullet(cfg["ALERT_API_KEY"])
        self.title = cfg["APP_NAME"]
    
    def send_alert(self, message):
        """envoie une alerte sur les équipements déclarés dans le compte pushbullet"""
        devices = self.pb.getDevices()
        for device in devices:
            if device['pushable']:
                note = self.pb.pushNote(device["iden"], self.title, message)
