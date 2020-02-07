from pushbullet.pushbullet import PushBullet
from modules.conf import read_conf, write_conf

class Alerteur():
    """classe de pilotage des alertes"""
    def __init__(self):
        self.CONF_FILE = "alerteur"
        self.read_config()
    
    def add_alert(self, type, message):
        """ajoute une alerte"""
        if not type in self.alertes:
            self.alertes[type] = message
            self.write_config()
            pb = PushBullet(self.api_key)
            devices = pb.getDevices()
            for device in devices:
               if device['pushable']:
                   note = pb.pushNote(device["iden"], self.title + " - " + type, message)

    def remove_alert(self, type, message):
        """supprime une alerte"""
        if type in self.alertes:
            del self.alertes[type]
            self.write_config()

    def read_config(self):
        """lit le fichier de configuration"""
        cfg = read_conf(self.CONF_FILE)
        self.api_key = cfg["ALERT_API_KEY"]
        self.title = cfg["APP_NAME"]
        if type(cfg["alertes"]) is dict:
            self.alertes = cfg["alertes"]
        else:
            self.alertes = dict()
    
    def write_config(self):
        """ecrit la configuration dans le fichier de configuration"""
        cfg = {
            'ALERT_API_KEY':self.api_key,
            'APP_NAME':self.title,
            'alertes':self.alertes
        }
        write_conf(self.CONF_FILE,cfg)
