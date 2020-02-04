import sys
from modules.porte import Porte,Stepper
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

if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    CFG = read_conf("global")

    stepper = Stepper(CFG['PORTE_STEPPER_1'],CFG['PORTE_STEPPER_2'],CFG['PORTE_STEPPER_3'],CFG['PORTE_STEPPER_4'])
    porte = Porte(stepper,CFG['PORTE_PIN_BAS'],CFG['PORTE_PIN_HAUT'])

    cmd_open = '/home/pi/poulailler-console/porte_auto.sh open'
    cmd_close = '/home/pi/poulailler-console/porte_auto.sh close'

    if len(sys.argv) > 1:
        # la porte doit etre actionnee
        action = sys.argv[1]

        if action == "open":
            print("Porte en cours d'ouverture...")
            porte.open()
        elif action == "close":
            print("Porte en cours de fermeture...")
            porte.close()
    
    # ephemeride sur la localisation du poulailler
    s=Sun(lat=CFG['LATITUDE'],long=CFG['LONGITUDE'])

    # prochain lever de soleil
    print("Definition du prochain lever de soleil...")
    d_sunrise = datetime.now(tzlocal())
    next_sunrise = s.sunrise(d_sunrise)
    if next_sunrise < d_sunrise.time():
        d_sunrise = d_sunrise + timedelta(days=1)
        next_sunrise = s.sunrise(d_sunrise)
    open_next_date = datetime.combine(d_sunrise.date(),next_sunrise)

    # prochain coucher de soleil
    print("Definition du prochain coucher de soleil...")
    d_sunset = datetime.now(tzlocal())
    next_sunset = s.sunset(d_sunset)
    if next_sunset < d_sunset.time():
        d_sunset = d_sunset + timedelta(days=1)
        next_sunset = s.sunset(d_sunset)
    close_next_date = datetime.combine(d_sunset.date(),next_sunset)

    # mise à jour du cron
    print("Mise a jour des taches planifiees...")
    cron = CronTab(user=True)

    job_open = get_job(cron, cmd_open)
    job_open.setall(open_next_date)

    job_close = get_job(cron, cmd_close)
    job_close.setall(close_next_date)

    cron.write(user=True)

    # mise à jour de la configuration de la porte
    print("Mise a jour de la configuration de la porte...")
    porte.open_next_date = open_next_date.strftime("%Y-%m-%d %H:%M:%S")
    porte.close_next_date = close_next_date.strftime("%Y-%m-%d %H:%M:%S")
    porte.write_config()

    print("Taches effectuees avec succes.")