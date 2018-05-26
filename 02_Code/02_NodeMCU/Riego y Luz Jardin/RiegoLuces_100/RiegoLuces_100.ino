#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

//Our Wi-Fi ssdid and password
char* ssid = "Orozco_Network"; //Put your Wi-Fi ssdid here
char* password = "05062013"; //Your Wi-Fi Password
//char* ssid = "INFINITUM8500"; //Put your Wi-Fi ssdid here
//char* password = "1HfaNG4F3H"; //Your Wi-Fi Password
String riego_excedente = "0";
String riego_patio = "0";
String riego_frente = "0";
String luces = "0";

// NETWORK: to setup Static IP
IPAddress ip(192, 168, 1, 100); //example 1,100 -- REPLACE x,x
IPAddress gateway(192, 168, 1, 254); // 1, 254 -- REPLACE x,x
IPAddress subnet(255, 255, 255, 0);

ESP8266WebServer server; //server variable

void setup() {
  initializePin(); //call function
  
  // Static IP Setup
  WiFi.config(ip, gateway, subnet);

  //Making Connection With netword
  WiFi.begin(ssid, password);
  
  //Serial.begin(115200);
  //Serial.print("Searching Connection");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  
  Serial.println("");
  Serial.print("IP Address: "); //Show the IP Address to access your NodeMCU
  Serial.print(WiFi.localIP());
  
  serverSection();
}

void loop() {
  // put your main code here, to run repeatedly:
  server.handleClient();

}

void initializePin(){
  
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);

  digitalWrite(D1, HIGH);
  digitalWrite(D2, HIGH);
  digitalWrite(D3, HIGH);
  digitalWrite(D4, HIGH);
}

void serverSection(){
  server.on("/", []() {
    server.send(200, "text/html", "<!DOCTYPE html><html><meta charset='UTF-8'><head></head><body><h2>Orozco House</h2><h3><a href='/riego_excedente'>riego excedente</a></h3><br><h3><a href='/riego_patio'>riego patio</a></h3><br><h3><a href='/riego_frente'>riego frente</a></h3><br><h3><a href='/luces'>luces</a></h3><br></body></html>");
  });

  server.on("/riego_excedente", riego_excedente_state);
  server.on("/riego_patio", riego_patio_state);
  server.on("/riego_frente", riego_frente_state);
  server.on("/luces", luces_state);

  server.on("/status", all_state);
  
  server.begin();
}

void riego_excedente_state(){
  if(riego_excedente == "0"){
    riego_excedente = "1";
    digitalWrite(D1, LOW);
    server.send(200, "text/html", riego_excedente);
  }else{
    riego_excedente = "0";
    digitalWrite(D1, HIGH);
    server.send(200, "text/html", riego_excedente);
  }
}

void riego_patio_state(){
  if(riego_patio == "0"){
    riego_patio = "1";
    digitalWrite(D2, LOW);
    server.send(200, "text/html", riego_patio);
  }else{
    riego_patio = "0";
    digitalWrite(D2, HIGH);
    server.send(200, "text/html", riego_patio);
  }
}

void riego_frente_state(){
  if(riego_frente == "0"){
    riego_frente = "1";
    digitalWrite(D3, LOW);
    server.send(200, "text/html", riego_frente);
  }else{
    riego_frente = "0";
    digitalWrite(D3, HIGH);
    server.send(200, "text/html", riego_frente);
  }
}

void luces_state(){
  if(luces == "0"){
    luces = "1";
    digitalWrite(D4, LOW);
    server.send(200, "text/html", luces);
  }else{
    luces = "0";
    digitalWrite(D4, HIGH);
    server.send(200, "text/html", luces);
  }
}

void all_state(){
  server.send(200, "text/html", "{\"riego_excedente\":\""+riego_excedente+"\",\"riego_patio\":\""+riego_patio+"\",\"riego_frente\":\""+riego_frente+"\",\"luces\":\""+luces+"\"}");
}


