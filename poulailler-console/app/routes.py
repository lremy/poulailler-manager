from flask import render_template, flash, redirect, url_for, request
from app import app
from RPi import GPIO
from modules.porte import Porte, Stepper

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

stepper = Stepper(3,4,5,6)
porte = Porte(stepper,23,24)

# page par defaut, redirection vers la page principale
@app.route('/')
def index():
    return redirect(url_for('board'))

# page principale
@app.route('/board')
def board():
    return render_template('board.html')

# module porte
@app.route('/porte', methods= ['POST','GET'])
def url_porte():
    img_etat = "ouverte"
    img_action = "fermer"
    if request.method == 'POST':
        # demande de modification de l'etat de la porte
        if porte.is_closed():
            # la porte est fermee
            porte.open()
        elif porte.is_opened():
            # la porte est ouverte
            porte.close()
    if porte.is_closed():
        # la porte est fermee
        img_etat = "fermee"
        img_action = "ouvrir"
    elif not porte.is_opened():
        # la porte n'est pas ouverte = porte en deplacement
        img_etat = "enCours"
        img_action = "en cours"
    template_data = {
        'img_etat' : img_etat,
        'img_action' : img_action
    }
    return render_template('porte.html', **template_data)
