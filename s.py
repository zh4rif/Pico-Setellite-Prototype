from imu import MPU6050
from time import sleep
from machine import Pin, I2C
import socket
import network
import bme280
import requests
from umqtt.simple import MQTTClient
led = Pin(13, Pin.OUT)
led2 = Pin(14, Pin.OUT)
led3 = Pin(12, Pin.OUT)
server_url = "http://10.27.29.93/"
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=100000)
imu = MPU6050(i2c)

wifi_ssid = "FTKEE STEM LAB"
wifi_password = "steml@b2023"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while not wlan.isconnected():
    print('Waiting for connection...')
    sleep(1)
ip = wlan.ifconfig()[0]
print(f'Connected on {ip}')

mqtt_host = "io.adafruit.com"
mqtt_username = "zh4rif098"  # Your Adafruit IO username
mqtt_password = "aio_hyfk73yatNmyW46A2j6iQEV7qRLU"  # Adafruit IO Key
temp_feed = "Temperature"  # The MQTT topic for your Adafruit IO Feed
humid_feed = "Humudity"
pressure_feed = "Pressure"

mqtt_client_id = "aio_hyfk73yatNmyW46A2j6iQEV7qRLU"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

mqtt_client.connect()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

page = open("sensor.html", "r")
html = page.read()
page.close()



def get_sensor_data():
    ax, ay, az = round(imu.accel.x, 2), round(imu.accel.y, 2), round(imu.accel.z, 2)
    gx, gy, gz = round(imu.gyro.x), round(imu.gyro.y), round(imu.gyro.z)
    bme = bme280.BME280(i2c=i2c)
    temp  = bme.values[0]
    pressure = bme.values[1]
    humidity = bme.values[2]
    data = {
        "accX": ax,
        "accY": ay,
        "accZ": az,
        "gyroX": gx,
        "gyroY": gy,
        "gyroZ": gz,
        "temperature": temp,
        "pressure": pressure,
        "humidity": humidity
    }
    return data



def serve(connection):
    while True:
        client, addr = connection.accept()
        request = client.recv(1024).decode('utf-8')
        request_line = request.split(' ')[1]
        
        print("Request:", request_line)

        if request_line == '/data':
            data = get_sensor_data()
            response = json.dumps(data)
            client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n".encode())
            client.send(response.encode())
        else:
            data = get_sensor_data()
            response = webpage(data)
            client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode())
            client.send(response.encode())
        
        client.close()
        
        
while True:
    cl, addr = s.accept()
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    response = html

    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
    
    sensor_data = get_sensor_data()
    
    try:
        response = requests.post(server_url, json=sensor_data)
        print("Data sent successfully")
        print("Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", e)
    
    ax = round(imu.accel.x, 2)
    ay = round(imu.accel.y, 2)
    az = round(imu.accel.z, 2)
    gx = round(imu.gyro.x)
    gy = round(imu.gyro.y)
    gz = round(imu.gyro.z)
    tem = round(imu.temperature)
    bme = bme280.BME280(i2c=i2c)
    temp  = bme.values[0]
    pressure = bme.values[1]
    humidity = bme.values[2]
    print("\tax", ax, "\tay", ay ,"\taz", az ,"\tgx",gx,"\tgy",gy,"\tgz",gz,"\tTemperature", tem,"\thumidity",humidity,"\tPressure",pressure)
    temp_message=str(tem) #Change temperature to string
    humidity_message=str(humidity)
    pressure_message=str(pressure)
    temp=temp_message.replace('C','') #Remove "C" Symbol
    mqtt_client.publish(temp_feed, temp) #Publish
    mqtt_client.publish(pressure_feed_feed, pressure)
    mqtt_client.publish(humid_feed_feed, humidity)


    count = 0  # Resetting count here, if it's meant to count sensor readings.

    file = open("data.txt", "a")
    file.write(str(count) + "," + str(ax) + "," + str(ay) + "," + str(az) + "," + str(gx) + "," + str(gy) + "," +
               str(gz) + "," + str(tem) + "\n")
    file.close()

    # GPIO control based on sensor readings
    led.value(ax >= 0.7)
    led2.value(ay >= 0.7)
    led3.value(az >= 0.7)

    sleep(1)