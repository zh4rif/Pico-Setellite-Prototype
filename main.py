from imu import MPU6050
import bme280
from time import sleep
from machine import Pin, I2C
import time
import network
import socket
import json
led= Pin(13,Pin.OUT)
led2= Pin(14,Pin.OUT)
led3= Pin(12,Pin.OUT)


page = open("index.html", "r")
html = page.read()
page.close()
i2c =I2C( 1, sda=Pin(2),scl=Pin(3),freq=100000)
imu =MPU6050(i2c)

wifi_ssid = "FTKEE STEM LAB"
wifi_password = "steml@b2023"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
ip = wlan.ifconfig()[0]
print("Connected to WiFi")
print(f'Connected on {ip}')
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)



def serve(connection):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:

            pass

        print(request)

        if request == '/data':


            ax,ay,az,gx,gy,gz = get_mpu6050_data
            

            response = html


            client.send(json.dumps(response))


        else:


            html = page(0, 0)  # Initial values for temperature and humidity


            client.send(html)

        client.close()    



def open_socket(ip):


    # Open a socket


    address = (ip, 80)


    connection = socket.socket()


    connection.bind(address)


    connection.listen(1)


    print(connection)


    return connection


try:
    
    file = open("data.txt","a")
    
    if ip is not None:


        connection = open_socket(ip)


        serve(connection)
except OSError:
                
    file =open("data.txt","w")
 
count = 0


while True:
    ax = round(imu.accel.x,2)
    ay = round(imu.accel.y,2)
    az = round(imu.accel.z,2)
    gx = round(imu.gyro.x)
    gy = round(imu.gyro.y)
    gz = round(imu.gyro.z)
    tem = round(imu.temperature, )
    bme = bme280.BME280(i2c=i2c)
    temp  = bme.values[0]
    pressure = bme.values[1]
    humidity = bme.values[2]
    
    print("\tax", ax, "\tay", ay ,"\taz", az ,"\tgx",gx,"\tgy",gy,"\tgz",gz,"\tTemperature", tem,"\thumidity",humidity,"\tPressure",pressure)
    
    file.write(str(count)+","+str(ax)+","+str(ay)+","+str(az)+","+str(gx)+","+str(gy)+","+str(gz)+","+str(tem)+"\n")
    file.flush()
    count+=1

   
#test gyro
    if ax>=0.7:
        led.on()
        
    else:
         led.off()

    if ay>=0.7:
        led2.on()
        
    else:
         led2.off()

    if az>=0.7:
        led3.on()
        
    else:
         led3.off()
    sleep(1)