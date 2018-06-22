#!/usr/bin/python

from flask import request
from flask_api import FlaskAPI
import time
import urllib.request
import threading
import mysql.connector
import json
import requests
import hashlib
import hmac
import base64
import datetime
import urllib.parse
from dateutil.parser import parse

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

hostname = 'localhost'
dbUsr = 'IoTHouse_usr'
dbPsw = 'IoTHouse_PsW1@'
dbDB = 'IoT_House'
Coon = None
Usr = None

def getConnectDB():
    try:
        global Coon
        if not Coon:
            Coon = mysql.connector.connect(host = hostname, user = dbUsr, password = dbPsw, database = dbDB)
            Coon.start_transaction(isolation_level='READ COMMITTED')
            print("Conexion a BD correcta")
        return Coon
    except mysql.connector.Error as err:
        print("Conexion a BD fallida")
        
def getSHA256_Token(strMessage):
    message = bytes(strMessage,'utf-8')
    secret = bytes('iCAN_ScT','utf-8')

    signature = base64.b64encode(hmac.new(secret, message, digestmod = hashlib.sha256).digest())
    return signature

def validToken(strToken, strTypeWS):
    
    # Return values
    #  0 - OK
    #  1 - No tokens
    #  2 - Credential type NOT equal
    #  3 - Connection problems
    
    auCoon = getConnectDB()
    if not auCoon:
        return "3"
    else:
        Curs = auCoon.cursor()
        #strQuery = "SELECT Credentials.CredentialID, Credentials.CredentialType FROM Credentials inner join (SELECT CredentialID  FROM Tokens WHERE token = '" + strToken + "' AND tDate > DATE_SUB(CURDATE(), INTERVAL 1 DAY)) as CredToken On Credentials.CredentialID = CredToken.CredentialID"
        strQuery = "SELECT users.user_id, users.user_user_types_id FROM users inner join (SELECT token_user_id  FROM tokens WHERE token = '" + strToken + "' AND tokens.token_datetime > DATE_SUB(CURDATE(), INTERVAL 1 DAY)) as UserToken On users.user_id = UserToken.token_user_id"
        #print (strQuery)
        Curs.execute(strQuery)
        iRegisters = 0
        
        for (user_id, user_user_types_id) in Curs:
            iRegisters = iRegisters + 1
            Usr = user_id
            CredType = user_user_types_id
        
        if (iRegisters == 0):
            return 1 # No tokens
        
        if (CredType != strTypeWS):
            return 2 # Credential type NOT equal

        if (iRegisters == 1):
            return 0 # OK
    
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
    global boSuspendeLuzJardin
    
    #=========================================================
    print("tiempo luces jardin: " + str(iTiempoLuzJardin))
    if iTiempoLuzJardin > 0 and not boSuspendeLuzJardin:
    
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
    print("tiempo Frente: " + str(iTiempoRiegoFrente))
    if iTiempoRiegoFrente > 0 and not boSuspenderRiego :
        
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
    print("tiempo excedente: " + str(iTiempoRiegoExcedente))
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
    print("tiempo patio: " + str(iTiempoRiegoPatio))
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
    
@app.route('/user_login/<JsonAuthenData>',methods=['GET','POST'])
def user_login(JsonAuthenData):
    #=== Load Json Data
    jAuthenData = json.loads(JsonAuthenData)
    
    #=== Valid Json Data
    strPsw = jAuthenData['user_psw']
    if(len(strPsw) > 20):
        return  "{\"status\":\"fail\",\"error\":\"Psw len  is bigger than limit - 20 characters\"}"
    strUsr = jAuthenData['user_usr']
    if(len(strUsr) > 20):
        return  "{\"status\":\"fail\",\"error\":\"Usr len  is bigger than limit - 20 characters\"}"
    
    strdecode_Usr = urllib.parse.unquote_plus(strUsr)
    strdecode_Psw = urllib.parse.unquote_plus(strPsw)
    
    #=== Valid DB Connection
    auCoon = getConnectDB()
    if not auCoon:
        return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
    else:
        #=== Valid user
        Curs = auCoon.cursor()
        strQuery = "SELECT user_id, user_user_types_id FROM users WHERE user_usr = '{}' AND user_psw = '{}'".format(strdecode_Usr, strdecode_Psw)
        Curs.execute(strQuery)
        iRegisters = 0
        for (user_id, user_user_types_id) in Curs:
            #=== create token
            while True:
                token = {}
                token['DcID'] = user_id
                token['EndDate'] = datetime.datetime.now()
                strToken = json.dumps(token,default=datetime_handler)
                strToken = getSHA256_Token(strToken)
                strToken = strToken.decode(encoding = 'utf-8')
                if strToken.find("\\") == -1:
                    if strToken.find("/") == -1:
                        break;
                    
            #=== Insert token  in DB for user
            strQuery = ("INSERT INTO tokens (token_datetime, token,token_user_id) VALUES ('{}','{}',{})".format(datetime.datetime.now().isoformat(),strToken,user_id))             
            iRegisters = iRegisters + 1
            try:
                Curs.execute(strQuery)
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to execute sql query\"}"
            
            #=== Create OK response Json
            strToken = "{\"status\":\"success\",\"token\":\"" + strToken.strip() + "\",\"user_types_id\":\"" + str(user_user_types_id) + "\",\"user_id\":\"" + str(user_id) + "\"}"

        Curs.close()
        auCoon.commit()
    
    #=== Create Errors response Json
    if iRegisters == 0:
        strToken = "{\"status\":\"fail\",\"error\":\"Invalid User\"}"
    if iRegisters > 1:
        strToken = "{\"status\":\"fail\",\"error\":\"User with more than one register\"}"
    
    # Return Json response
    return strToken
    
@app.route('/insert_pantry_category/<Json>')
def insert_pantry_category(Json):
    #=== Load Json Data
    JsonData = json.loads(Json)
    
    #=== Valid Json Data
    strToken = JsonData['token']
    if(len(strToken) > 255):
        return  "{\"status\":\"fail\",\"error\":\"Token size  is bigger than limit - 255 characteres\"}"
    strCategoryName = JsonData['category_name']
    if(len(strCategoryName) > 20):
        return  "{\"status\":\"fail\",\"error\":\"Category name size  is bigger than limit - 20 characteres\"}"    
    
    #=== Valid Token
    valiTokenResponse = validToken(strToken,1) # 1 = Client App  // DaOr -- could be used by 4 and 1 ??
    if (valiTokenResponse == 0): # 0 = OK 
        #=== Valid DB Connection
        auCoon = getConnectDB()
        if not auCoon:
            return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
        else:
            #=== Insert order in DB
            strQuery = ("INSERT INTO pantry_categories (pantry_category_name) VALUES ('{}')".format(strCategoryName))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()

                return  "{\"status\":\"success\"}"
            
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to create category in DB\"}"
    elif(valiTokenResponse==1):
        return  "{\"status\":\"fail\",\"error\":\"Invalid Token\"}"
    elif(valiTokenResponse==2): 
        return  "{\"status\":\"fail\",\"error\":\"Invalid WS for APP\"}"   
    elif(valiTokenResponse==3):
        return  "{\"status\":\"fail\",\"error\":\"Network connection problems\"}"

@app.route('/delete_pantry_category/<Json>')
def delete_pantry_category(Json):
    #=== Load Json Data
    JsonData = json.loads(Json)
    
    #=== Valid Json Data
    strToken = JsonData['token']
    if(len(strToken) > 255):
        return  "{\"status\":\"fail\",\"error\":\"Token size  is bigger than limit - 255 characteres\"}"
    strPantryCategoryId = JsonData['pantry_category_id']
    if (strPantryCategoryId.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryCategoryId is not in number format\"}"
     
    
    #=== Valid Token
    valiTokenResponse = validToken(strToken,1) # 1 = Client App  // DaOr -- could be used by 4 and 1 ??
    if (valiTokenResponse == 0): # 0 = OK 
        #=== Valid DB Connection
        auCoon = getConnectDB()
        if not auCoon:
            return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
        else:
            #=== Delete pantry products that are from this strPantryCategoryId
            strQuery = ("DELETE FROM pantry_products WHERE pantry_product_pantry_category_id = {}".format(strPantryCategoryId))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to create product in DB\"}"
                
            #=== Delete pantry category
            strQuery = ("DELETE FROM pantry_categories WHERE pantry_category_id = {}".format(strPantryCategoryId))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()

                return  "{\"status\":\"success\"}"
            
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error delete pantry category in DB\"}"
    elif(valiTokenResponse==1):
        return  "{\"status\":\"fail\",\"error\":\"Invalid Token\"}"
    elif(valiTokenResponse==2): 
        return  "{\"status\":\"fail\",\"error\":\"Invalid WS for APP\"}"   
    elif(valiTokenResponse==3):
        return  "{\"status\":\"fail\",\"error\":\"Network connection problems\"}"

@app.route('/insert_pantry_product/<Json>')
def insert_pantry_product(Json):
    #=== Load Json Data
    JsonData = json.loads(Json)
    
    #=== Valid Json Data
    strToken = JsonData['token']
    if(len(strToken) > 255):
        return  "{\"status\":\"fail\",\"error\":\"Token size  is bigger than limit - 255 characteres\"}"
    strPantryProductName = JsonData['pantry_product_name']
    if(len(strCategoryName) > 20):
        return  "{\"status\":\"fail\",\"error\":\"Category name size  is bigger than limit - 20 characteres\"}"
    strPantryCategoryId = JsonData['pantry_pantry_category_id']
    if (strPantryCategoryId.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"Pantry_category_id is not in number format\"}"
     
    
    #=== Valid Token
    valiTokenResponse = validToken(strToken,1) # 1 = Client App  // DaOr -- could be used by 4 and 1 ??
    if (valiTokenResponse == 0): # 0 = OK 
        #=== Valid DB Connection
        auCoon = getConnectDB()
        if not auCoon:
            return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
        else:
            #=== Insert order in DB
            strQuery = ("INSERT INTO pantry_products (pantry_product_name, pantry_pantry_category_id) VALUES ('{}',{})".format(strCategoryName,strPantryCategoryId))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()

                return  "{\"status\":\"success\"}"
            
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to create product in DB\"}"
    elif(valiTokenResponse==1):
        return  "{\"status\":\"fail\",\"error\":\"Invalid Token\"}"
    elif(valiTokenResponse==2): 
        return  "{\"status\":\"fail\",\"error\":\"Invalid WS for APP\"}"   
    elif(valiTokenResponse==3):
        return  "{\"status\":\"fail\",\"error\":\"Network connection problems\"}"
    
@app.route('/delete_pantry_product/<Json>')
def delete_pantry_product(Json):
    #=== Load Json Data
    JsonData = json.loads(Json)
    
    #=== Valid Json Data
    strToken = JsonData['token']
    if(len(strToken) > 255):
        return  "{\"status\":\"fail\",\"error\":\"Token size  is bigger than limit - 255 characteres\"}"
    strPantryProductId = JsonData['pantry_product_id']
    if (strPantryProductId.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryProductId is not in number format\"}"
     
    
    #=== Valid Token
    valiTokenResponse = validToken(strToken,1) # 1 = Client App  // DaOr -- could be used by 4 and 1 ??
    if (valiTokenResponse == 0): # 0 = OK 
        #=== Valid DB Connection
        auCoon = getConnectDB()
        if not auCoon:
            return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
        else:
            #=== Insert order in DB
            strQuery = ("DELETE FROM pantry_products WHERE pantry_product_id = {}".format(strPantryProductId))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()

                # === DaOr-- products should be ordered

                return  "{\"status\":\"success\"}"
            
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to create product in DB\"}"
    elif(valiTokenResponse==1):
        return  "{\"status\":\"fail\",\"error\":\"Invalid Token\"}"
    elif(valiTokenResponse==2): 
        return  "{\"status\":\"fail\",\"error\":\"Invalid WS for APP\"}"   
    elif(valiTokenResponse==3):
        return  "{\"status\":\"fail\",\"error\":\"Network connection problems\"}"
    
@app.route('/update_pantry_product/<Json>')
def update_pantry_product(Json):
    #=== Load Json Data
    JsonData = json.loads(Json)
    
    #=== Valid Json Data
    strToken = JsonData['token']
    if(len(strToken) > 255):
        return  "{\"status\":\"fail\",\"error\":\"Token size  is bigger than limit - 255 characteres\"}"
    strPantryProductId = JsonData['pantry_product_id']
    if (strPantryProductId.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryProductId is not in number format\"}"
    strPantryCategoryNeed = JsonData['pantry_product_needed']
    if (strPantryCategoryNeed.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryCategoryNeed is not in number format\"}"
    strPantryProductAisle = JsonData['pantry_product_aisle']
    if (strPantryProductAisle.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryProductAisle is not in number format\"}"
    
    #=== Valid Token
    valiTokenResponse = validToken(strToken,1) # 1 = Client App  // DaOr -- could be used by 4 and 1 ??
    if (valiTokenResponse == 0): # 0 = OK 
        #=== Valid DB Connection
        auCoon = getConnectDB()
        if not auCoon:
            return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
        else:
            #=== update pantry product
            strQuery = ("UPDATE pantry_products  SET  pantry_product_needed = {}, pantry_product_order = {}, pantry_product_aisle = {} WHERE pantry_product_id = {}".format(pantry_product_needed,pantry_product_order,pantry_product_aisle,strPantryProductId))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()

                return  "{\"status\":\"success\"}"
            
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to update pantry product DB\"}"
    elif(valiTokenResponse==1):
        return  "{\"status\":\"fail\",\"error\":\"Invalid Token\"}"
    elif(valiTokenResponse==2): 
        return  "{\"status\":\"fail\",\"error\":\"Invalid WS for APP\"}"   
    elif(valiTokenResponse==3):
        return  "{\"status\":\"fail\",\"error\":\"Network connection problems\"}"
    
@app.route('/change_category_pantry_product/<Json>')
def change_category_pantry_product(Json):
    #=== Load Json Data
    JsonData = json.loads(Json)
    
    #=== Valid Json Data
    strToken = JsonData['token']
    if(len(strToken) > 255):
        return  "{\"status\":\"fail\",\"error\":\"Token size  is bigger than limit - 255 characteres\"}"
    strPantryProductId = JsonData['pantry_product_id']
    if (strPantryProductId.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryProductId is not in number format\"}"
    strPantryPantryCategoryId = JsonData['pantry_pantry_category_id']
    if (strPantryPantryCategoryId.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryPantryCategoryId is not in number format\"}"

    #=== Valid Token
    valiTokenResponse = validToken(strToken,1) # 1 = Client App  // DaOr -- could be used by 4 and 1 ??
    if (valiTokenResponse == 0): # 0 = OK 
        #=== Valid DB Connection
        auCoon = getConnectDB()
        if not auCoon:
            return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
        else:
            #=== get last order number from category to change
            
            #=== update pantry product
            strQuery = ("UPDATE pantry_products SET  strPantryPantryCategoryId = {} WHERE pantry_product_id = {}".format(pantry_pantry_category_id,strPantryProductId))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()

                return  "{\"status\":\"success\"}"
            
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to update pantry product DB\"}"
    elif(valiTokenResponse==1):
        return  "{\"status\":\"fail\",\"error\":\"Invalid Token\"}"
    elif(valiTokenResponse==2): 
        return  "{\"status\":\"fail\",\"error\":\"Invalid WS for APP\"}"   
    elif(valiTokenResponse==3):
        return  "{\"status\":\"fail\",\"error\":\"Network connection problems\"}"

@app.route('/update_order_pantry_product/<Json>')
def update_order_pantry_product(Json):
    #=== Load Json Data
    JsonData = json.loads(Json)
    
    #=== Valid Json Data
    strToken = JsonData['token']
    if(len(strToken) > 255):
        return  "{\"status\":\"fail\",\"error\":\"Token size  is bigger than limit - 255 characteres\"}"
    strPantryProductId = JsonData['pantry_product_id']
    if (strPantryProductId.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryProductId is not in number format\"}"
    strPantryProductOrder = JsonData['pantry_product_order']
    if (strPantryProductOrder.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryProductOrder is not in number format\"}"
    strPantryProductMove = JsonData['pantry_product_move']
    if (strPantryProductMove.isdigit() == False):
        return  "{\"status\":\"fail\",\"error\":\"strPantryProductAisle is not in number format\"}"
    
    #=== Valid Token
    valiTokenResponse = validToken(strToken,1) # 1 = Client App  // DaOr -- could be used by 4 and 1 ??
    if (valiTokenResponse == 0): # 0 = OK 
        #=== Valid DB Connection
        auCoon = getConnectDB()
        if not auCoon:
            return  "{\"status\":\"fail\",\"error\":\"Problem with DB connection\"}"
        else:
            #=== update pantry product
            strQuery = ("UPDATE pantry_products  SET  pantry_product_needed = {}, pantry_product_order = {}, pantry_product_aisle = {} WHERE pantry_product_id = {}".format(pantry_product_needed,pantry_product_order,pantry_product_aisle,strPantryProductId))             
            try:
                Curs = auCoon.cursor()
                Curs.execute(strQuery)
                auCoon.commit()

                return  "{\"status\":\"success\"}"
            
            except:
                return   "{\"status\":\"fail\",\"error\":\"Error to update pantry product DB\"}"
    elif(valiTokenResponse==1):
        return  "{\"status\":\"fail\",\"error\":\"Invalid Token\"}"
    elif(valiTokenResponse==2): 
        return  "{\"status\":\"fail\",\"error\":\"Invalid WS for APP\"}"   
    elif(valiTokenResponse==3):
        return  "{\"status\":\"fail\",\"error\":\"Network connection problems\"}"
    

    
if __name__ == "__main__":
    time.sleep(5)
    Estatus()
    VerifyExistSB()
    print("despues de 5 sec")
    app.run()

