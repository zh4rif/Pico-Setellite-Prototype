import network
import socket
from machine import Pin
import ure

# Initialize LED
led = Pin(15, Pin.OUT)

# Connect to Wi-Fi
ssid = 'FTKEE STEM LAB' #Your network name
password = 'steml@b2023' #Your WiFi password

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
while not wlan.isconnected():
    pass

print('Connection successful')
print(wlan.ifconfig())

# HTML content to serve
html = """<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Pico LED Control</title>
</head>
<body>
    <h1>Control LED</h1>
    <button onclick="toggleLED()">Toggle LED</button>
    <script>
        function toggleLED() {
            fetch('/toggle')
            .then(response => response.text())
            .then(data => console.log(data));
        }
    </script>
</body>
</html>
"""

# Setup server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

# Listen for connections
while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    request = cl.recv(1024)
    request = str(request)
    print('Request:', request)
    
    # Parse request
    if '/toggle' in request:
        led.value(not led.value())
        response = 'LED state: {}'.format('ON' if led.value() else 'OFF')
    else:
        response = html
    
    cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()