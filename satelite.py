import tkinter as tk
import math
from mpu6050 import mpu6050
import time
from smbus2 import SMBus
from tkinter import messagebox
import bme280
import smbus2
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Initialize MPU6050
address_mpu6050 = 0x68
sensor = mpu6050(address_mpu6050)

# MPU6050 Register Addresses
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# Initialize BME280
address_bme280 = 0x76
bus = smbus2.SMBus(1)
calibration_params = bme280.load_calibration_params(bus, address_bme280)

# Initialize main window
root = tk.Tk()
root.title("Satellite")
root.geometry("800x800")

# Canvas for drawing
canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack()

# Labels for sensor readings
temp_label = tk.Label(root, text="Temperature:")
temp_label.pack()
humidity_label = tk.Label(root, text="Humidity:")
humidity_label.pack()
pressure_label = tk.Label(root, text="Pressure:")
pressure_label.pack()
accel_label = tk.Label(root, text="Accelerometer:")
accel_label.pack()
gyro_label = tk.Label(root, text="Gyroscope:")
gyro_label.pack()

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("sdp-422806-11c1654b7049.json", scope)
client = gspread.authorize(creds)

def list_spreadsheets():
    sheets = client.openall()
    for sheet in sheets:
        print(sheet.title)

# Uncomment the line below to list all accessible spreadsheets
list_spreadsheets()

spreadsheet = client.open("Satelite_data").sheet1  # Open the first sheet

def read_raw_data(addr):
    high = bus.read_byte_data(address_mpu6050, addr)
    low = bus.read_byte_data(address_mpu6050, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

sending_data = False

def toggle_sending_data():
    global sending_data
    sending_data = not sending_data
    if sending_data:
        start_button.config(text="Stop Sending Data")
    else:
        start_button.config(text="Start Sending Data")

def update_readings():
    # Read BME280 sensor data
    data = bme280.sample(bus, address_bme280, calibration_params)
    temperature_celsius = data.temperature
    humidity = data.humidity
    pressure = data.pressure
    
    # Read MPU6050 sensor data
    accel_x = read_raw_data(ACCEL_XOUT_H) / 16384.0
    accel_y = read_raw_data(ACCEL_YOUT_H) / 16384.0
    accel_z = read_raw_data(ACCEL_ZOUT_H) / 16384.0
    gyro_x = read_raw_data(GYRO_XOUT_H) / 131.0
    gyro_y = read_raw_data(GYRO_YOUT_H + 2) / 131.0
    gyro_z = read_raw_data(GYRO_ZOUT_H + 4) / 131.0

    # Convert temperature to Fahrenheit
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32

    # Update labels with sensor data
    temp_label.config(text=f"Temperature: {temperature_celsius:.2f}°C / {temperature_fahrenheit:.2f}°F")
    humidity_label.config(text=f"Humidity: {humidity:.2f}%")
    pressure_label.config(text=f"Pressure: {pressure:.2f}hPa")
    accel_label.config(text=f"Accelerometer: X={accel_x:.2f}, Y={accel_y:.2f}, Z={accel_z:.2f}")
    gyro_label.config(text=f"Gyroscope: X={gyro_x:.2f}, Y={gyro_y:.2f}, Z={gyro_z:.2f}")

    # Send data to Google Sheets if sending_data is True
    if sending_data:
        send_to_google_sheets(temperature_celsius, temperature_fahrenheit, humidity, pressure, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)

    root.after(2000, update_readings)

def send_to_google_sheets(temp_c, temp_f, humidity, pressure, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
    row = [
        time.strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
        temp_c,
        temp_f,
        humidity,
        pressure,
        accel_x,
        accel_y,
        accel_z,
        gyro_x,
        gyro_y,
        gyro_z
    ]
    spreadsheet.append_row(row)

def get_mpu_data():
    accel_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()

    # Calculate roll and pitch from accelerometer data
    roll = math.atan2(accel_data['y'], accel_data['z']) * 57.2958
    pitch = math.atan2(-accel_data['x'], math.sqrt(accel_data['y']**2 + accel_data['z']**2)) * 57.2958

    return roll, pitch

def draw_indicator():
    roll, pitch = get_mpu_data()

    # Clear the canvas
    canvas.delete("all")

    # Draw the horizon indicator
    center_x = 200
    center_y = 200
    radius = 150

    # Calculate the horizon line position based on pitch
    pitch_offset = pitch * (radius / 90)

    # Draw the upper half (sky)
    canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                      start=0, extent=180, fill="blue")

    # Draw the lower half (ground)
    canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                      start=180, extent=180, fill="brown")

    # Draw the horizon line
    canvas.create_line(center_x - radius, center_y + pitch_offset,
                       center_x + radius, center_y + pitch_offset, fill="yellow", width=2)

    # Draw roll lines
    for angle in range(-45, 46, 15):
        rad_angle = math.radians(angle + roll)
        line_length = 10 if angle % 30 == 0 else 5
        x_start = center_x + (radius - line_length) * math.sin(rad_angle)
        y_start = center_y - (radius - line_length) * math.cos(rad_angle)
        x_end = center_x + radius * math.sin(rad_angle)
        y_end = center_y - radius * math.cos(rad_angle)
        canvas.create_line(x_start, y_start, x_end, y_end, fill="white")

    # Draw the triangle indicator
    canvas.create_polygon(center_x, center_y - 10, center_x - 10, center_y + 10,
                          center_x + 10, center_y + 10, fill="orange")

    # Display roll and pitch values
    canvas.create_text(50, 380, text=f"ROLL: {roll:.2f}", fill="black")
    canvas.create_text(350, 380, text=f"PITCH: {pitch:.2f}", fill="black")

    # Update the canvas every 100 ms
    root.after(100, draw_indicator)

# Button to start/stop sending data
start_button = tk.Button(root, text="Start Storing Data", command=toggle_sending_data)
start_button.pack()

# Start updating sensor readings and drawing the indicator
update_readings()
draw_indicator()

# Start the Tkinter main loop
root.mainloop()
