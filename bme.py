#import modules
import network
import socket
from time import sleep
from machine import Pin, I2C
import bme280

ssid = 'Xiaomi 12 Lite' #Your network name
password = '88888888' #Your WiFi password

#initialize I2C 
i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(reading):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>Pico W Weather Station</title>
            <meta http-equiv="refresh" content="10">
            </head>
            <body>
            <p>{reading}</p>
            </body>
            </html>
            """
    return str(html)
    
def serve(connection):
    #Start a web server
    
    while True:
        bme = bme280.BME280(i2c=i2c)
        temp = bme.values[0]
        pressure = bme.values[1]
        humidity = bme.values[2]
        reading = 'Temperature: ' + temp + '. Humidity: ' + humidity + '. Pressure: ' + pressure
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)       
        html = webpage(reading)
        client.send(html)
        client.close()

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
    