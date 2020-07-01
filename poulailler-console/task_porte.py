import sys
from modules.porte_dc import PorteDC
from modules.luminosite_smbus import Luminosite
from modules.ephemeride import Sun
from modules.conf import read_conf
from crontab import CronTab
from datetime import datetime, timedelta
from dateutil.tz import *
from RPi import GPIO

def get_job(cron, cmd):
    job = ''
    jobs = cron.find_command(cmd)
    for j in jobs:
        job = j
    if job == '':
        job = cron.new(command=cmd)
    return job

def ouverture_porte():
    print("Porte en cours d'ouverture...")
    porte.open()

def fermeture_porte():
    print("Porte en cours de fermeture...")
    porte.close()

def decaler_heure():
    return datetime.now(tzlocal()) + timedelta(minutes=15)

def maj_job(action,next_date):
    cron = CronTab(user=True)
    job = get_job(cron, '/home/pi/poulailler-console/porte_auto.sh ' + action)
    job.setall(next_date)
    cron.write(user=True)

def should_open(action):
    return action == "open"

def is_lumi_open(niveau,seuil):
    return niveau > seuil

def is_lumi_close(niveau,seuil):
    return niveau < seuil

if __name__ == "__main__":

    if len(sys.argv) > 1:
        # porte à actionner
        action = sys.argv[1]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        porte = PorteDC()
        luminosite = Luminosite()

        # ephemeride sur la localisation du poulailler
        CFG = read_conf("global")
        s=Sun(lat=CFG['LATITUDE'],long=CFG['LONGITUDE'])

        if should_open(action):
            if is_lumi_open(luminosite.read_level,luminosite.seuil_ouverture):
                ouverture_porte()
                # prochain lever de soleil
                print("Definition du prochain lever de soleil...")
                d_sunrise = datetime.now(tzlocal())
                next_sunrise = s.sunrise(d_sunrise)
                if next_sunrise < d_sunrise.time():
                    d_sunrise = d_sunrise + timedelta(days=1)
                    next_sunrise = s.sunrise(d_sunrise)
                next_date = datetime.combine(d_sunrise.date(),next_sunrise)
                porte.open_next_date = next_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                next_date = decaler_heure()
        else:
            if is_lumi_close(luminosite.read_level,luminosite.seuil_fermeture):
                ouverture_porte()
                # prochain coucher de soleil
                print("Definition du prochain coucher de soleil...")
                d_sunset = datetime.now(tzlocal())
                next_sunset = s.sunset(d_sunset)
                if next_sunset < d_sunset.time():
                    d_sunset = d_sunset + timedelta(days=1)
                    next_sunset = s.sunset(d_sunset)
                next_date = datetime.combine(d_sunset.date(),next_sunset)
                porte.close_next_date = next_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                next_date = decaler_heure()
        maj_job (action,next_date)
        print("Mise a jour de la configuration de la porte...")
        porte.write_config()

    print("Tache effectuee avec succes.")