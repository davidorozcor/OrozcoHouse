#!/usr/bin/python

from flask import request
from flask_api import FlaskAPI
import RPi.GPIO as GPIO
import time
import urllib.request
import threading
import mysql.connector
import json
import requests

LEDS = {"green": 16, "red1": 18, "red2": 22}
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LEDS["green"], GPIO.OUT)
GPIO.setup(LEDS["red1"], GPIO.OUT)
GPIO.setup(LEDS["red2"], GPIO.OUT)

MCU_IP_Address = "192.168.1.100"

boRegando = False
boLucesEncendidads = False

boSuspenderRiego = False
boSuspendeLuzJardin = False

iTiempoRiegoExcedente = 0
iTiempoRiegoPatio = 0
iTiempoRiegoFrente = 0
iTiempoLuzJardin = 0

MCU_100_OnLine = False
MCU_101_OnLine = False

MCU_100_Riego_Frente_Status = False
MCU_100_Riego_Excedente_Status = False
MCU_100_Riego_Patio_Status = False
MCU_100_Luz_Jardin_Status = False

def Estatus():
    
    global MCU_100_OnLine 
    global MCU_101_OnLine
    
    global MCU_100_Riego_Frente_Status 
    global MCU_100_Riego_Excedente_Status 
    global MCU_100_Riego_Patio_Status 
    global MCU_100_Luz_Jardin_Status
    
    MCU_100_OnLine = False
    MCU_101_OnLine = False
    
    # MCU .100 Riego y Luces Jardin
    response = requests.get("http://" + MCU_IP_Address + "/status")
    if response.status_code == 200:
        
        MCU_100_OnLine = True
        print ("MCU 100 On Line")
        
        JsonData = response.json()
        
        MCU_100_Riego_Frente_Status = False
        MCU_100_Riego_Excedente_Status = False
        MCU_100_Riego_Patio_Status = False
        MCU_100_Luz_Jardin_Status = False
        
        if JsonData['luces'] == "0":
            MCU_100_Luz_Jardin_Status = False
            print ("MCU_100_Luz_Jardin_Status : False")
        else:
            MCU_100_Luz_Jardin_Status = True
            print ("MCU_100_Luz_Jardin_Status : True")
            
        if JsonData['riego_excedente'] == "0":
            MCU_100_Riego_Excedente_Status = False
            print ("MCU_100_Riego_Excedente_Status : False")
        else:
            MCU_100_Riego_Excedente_Status = True
            print ("MCU_100_Riego_Excedente_Status : True")
            
        if JsonData['riego_patio'] == "0":
            MCU_100_Riego_Patio_Status = False
            print ("MCU_100_Riego_Patio_Status : False")
        else:
            MCU_100_Riego_Patio_Status = True
            print ("MCU_100_Riego_Patio_Status : True")
            
        if JsonData['riego_frente'] == "0":
            MCU_100_Riego_Frente_Status = False
            print ("MCU_100_Riego_Frente_Status : False")
        else:
            MCU_100_Riego_Frente_Status = True
            print ("MCU_100_Riego_Frente_Status : True")
        
    else:
        MCU_100_OnLine = False
        print ("MCU 100 Off Line")

def LuzJardin():
    
    global iTiempoLuzJardin
    
    tCurrent = time.time()
    tStop = tCurrent + (iTiempoLuzJardin*60) #Multiplicado por 60 (segundos) para recibir minutos
    
    prendido = True
    while prendido and not boSuspendeLuzJardin:
        time.sleep(1) #Duerme por 1 segudo
        if tStop >= tCurrent:
            
            print("Luz Jardin restate: %d secs" % (tStop - time.time()))
            tCurrent = time.time()
            if boSuspendeLuzJardin == True:
                break

        else:
            prendido = False
    
    u = urllib.request.urlopen("http://" + MCU_IP_Address + "/luces")
    print("apaga luz jardin")


def inicia_riego():
    #def inicia_riego(JsonRutinaRiego):
    
    #JsonRutinaData = json.loads(JsonRutinaRiego)
    #iTiempoRiegoExcedente = JsonRutinaData['tiempo_riego_excedente']
    #iTiempoRiegoPatio = JsonRutinaData['tiempo_riego_patio']
    #iTiempoRiegoFrente = JsonRutinaData['tiempo_riego_frente']
    
    global iTiempoRiegoExcedente 
    global iTiempoRiegoPatio 
    global iTiempoRiegoFrente 
    
    global boSuspenderRiego
    global boRegando
    
    print("inica rutina de riego")
    
    #DaOr // Verifica status y apaga todo
    
    #=========================================================
    if iTiempoRiegoPatio > 0 and not boSuspenderRiego : 
        tCurrent = time.time()
        tStop = tCurrent + (iTiempoRiegoFrente*60) #Multiplicado por 60 (segundos) para recibir minutos
    
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_frente")
        print ("Riego frente prendido")
        
        prendido = True
        while prendido and not boSuspenderRiego:
            time.sleep(1) #Duerme por 1 segudo
            if tStop >= tCurrent: 
                print("Tiempo riego frente = %d" % (tStop - time.time()))
                tCurrent = time.time()
                if boSuspenderRiego == True:
                    break
            else:
                prendido = False
        
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_frente")
        print("Riego frente apagado")
    
    #=========================================================
    if iTiempoRiegoExcedente > 0 and not boSuspenderRiego:
        tCurrent = time.time()
        tStop = tCurrent + (iTiempoRiegoExcedente*60) #Multiplicado por 60 (segundos) para recibir minutos
    
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_excedente")
        print ("Riego excedente prendido")
        
        prendido = True
        while prendido and not boSuspenderRiego:
            time.sleep(1) #Duerme por 1 segudo
            if tStop >= tCurrent: 
                print("Tiempo riego excendente = %d" % (tStop - time.time()))
                tCurrent = time.time()
                if boSuspenderRiego == True:
                    break
            else:
                prendido = False
        
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_excedente")
        print("Riego excendente apagado")

    
    #=========================================================
    if iTiempoRiegoPatio > 0 and not boSuspenderRiego:
        tCurrent = time.time()
        tStop = tCurrent + (iTiempoRiegoPatio*60) #Multiplicado por 60 (segundos) para recibir minutos
    
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_patio")
        print ("Riego patio prendido")
        
        prendido = True
        while prendido and not boSuspenderRiego:
            time.sleep(1) #Duerme por 1 segudo
            if tStop >= tCurrent: 
                print("Tiempo riego patio = %d" % (tStop - time.time()))
                tCurrent = time.time()
                if boSuspenderRiego == True:
                    break
            else:
                prendido = False
        
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_patio")
        print("Riego patio apagado")
        
                
    ApagaRiego()
    
    boRegando = False
    boSuspenderRiego = False
    print ("rutina de riego terminada")
    
def ApagaRiego():
    
    Estatus()
    
    if MCU_100_Riego_Frente_Status == True:
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_frente")
        print ("Riego frente apagado")
    if MCU_100_Riego_Excedente_Status == True:
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_excedente")
        print ("Riego excedente apagado")
    if MCU_100_Riego_Patio_Status == True:
        u = urllib.request.urlopen("http://" + MCU_IP_Address + "/riego_patio")
        print ("Riego patio apagado")

app = FlaskAPI(__name__)

@app.route('/', methods=["GET"])
def api_root():
    return {
           "led_url": request.url + "led/(green | red)/",
      		 "led_url_POST": {"state": "(0 | 1)"}
    			 }

@app.route('/led/<color>/', methods=["GET", "POST"])
def api_leds_control2(color):
    print("inica rutina led")
    if request.method == "POST":
        if color in LEDS:
            
            GPIO.output(LEDS[color], int(request.data.get("state")))
        #u = urllib.request.urlopen("http://" + MCU_IP_Address + "/room_light")
        #print("Call room light")
    return {color: GPIO.input(LEDS[color])}

@app.route('/suspende_rutina_riego/', methods=["GET"])
def suspende_riego():
    global boSuspenderRiego
    global MCU_100_OnLine

    Estatus()
    if MCU_100_OnLine == True:
        boSuspenderRiego = True
        return {"rutina de riego suspendida":"yes"}
    
@app.route('/rutina_riego/<JsonRutinaRiego>', methods=["GET"])
def rutina_riego(JsonRutinaRiego):
    
    #t1 = threading.Thread(target=inicia_riego(JsonRutinaRiego))
    
    global iTiempoRiegoExcedente 
    global iTiempoRiegoPatio 
    global iTiempoRiegoFrente
    
    global MCU_100_OnLine
    global MCU_100_Riego_Frente_Status 
    global MCU_100_Riego_Excedente_Status 
    global MCU_100_Riego_Patio_Status
    
    global boRegando
    global boSuspenderRiego
    
    JsonRutinaData = json.loads(JsonRutinaRiego)
    iTiempoRiegoExcedente = JsonRutinaData['tiempo_riego_excedente']
    iTiempoRiegoPatio = JsonRutinaData['tiempo_riego_patio']
    iTiempoRiegoFrente = JsonRutinaData['tiempo_riego_frente']
    
    Estatus()
    
    #Apaga riego en caso de estar encendidas
    if MCU_100_OnLine == True and not boRegando:

        boRegando = True
        boSuspenderRiego = False
        ApagaRiego()
            
        tRiego = threading.Thread(target=inicia_riego)
        tRiego.start()
    
        #inicia_riego()
        print ("Riego iniciado")
        return {"Riego iniciado": "yes"}
        
    elif MCU_100_OnLine == False:
        print ("Error server 100")
        return {"status": "error server 100 no encontrado"}
    
    elif boRegando == True:
        print ("Rutina de riego en proceso")
        return {"status": "Rutina de riego en proceso"}

@app.route('/suspende_rutina_luz/', methods=["GET"])
def suspende_rutina_luz():
    
    global boSuspendeLuzJardin
    global MCU_100_OnLine
    global MCU_100_Luz_Jardin_Status

    Estatus()
    if MCU_100_OnLine == True:
        if MCU_100_Luz_Jardin_Status == True:
            boSuspendeLuzJardin = True
            print ("Luces suspendidas 1")
    
    print("Luces suspendidas")
    return {"status":"success"}
    
@app.route('/switch_light/<JsonRutinaData>', methods=["GET"])
def switch_light(JsonRutinaData):
    
    global iTiempoLuzJardin
    global MCU_100_OnLine
    global MCU_100_Luz_Jardin_Status
    
    JsonRutinaData = json.loads(JsonRutinaData)
    strLight = JsonRutinaData['Light']
    iTiempoLuzJardin = JsonRutinaData['Tiempo']

    #GetStatusLuzJardin
    Estatus()
    if MCU_100_OnLine == True:
        if MCU_100_Luz_Jardin_Status == False:
            u = urllib.request.urlopen("http://" + MCU_IP_Address + "/luces")
            print ("Luces prendidas 1")
        
        tLuzJardin = threading.Thread(target=LuzJardin)
        tLuzJardin.start()
        
        #inicia_riego()
        print ("Luces prendidas")
        return {"status": "success"}
    else:
        print ("Error server 100")
        return {"status": "error"}

if __name__ == "__main__":
    time.sleep(5)
    Estatus()
    print("despues de 5 sec")
    app.run()
