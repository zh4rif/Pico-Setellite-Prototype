import tkinter as tk
import math
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpu6050 import mpu6050
import smbus2
import bme280
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tkinter import messagebox
import tkintermapview
import threading

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
root.geometry("1200x1200")

# Create frames for the indicator and the graph
frame_left = tk.Frame(root, width=400, height=800)
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
frame_right = tk.Frame(root, width=800, height=1200)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Canvas for drawing the indicator
canvas = tk.Canvas(frame_left, width=400, height=400, bg="white")
canvas.pack()

# Labels for sensor readings
temp_label = tk.Label(frame_left, text="Temperature:")
temp_label.pack()
humidity_label = tk.Label(frame_left, text="Humidity:")
humidity_label.pack()
pressure_label = tk.Label(frame_left, text="Pressure:")
pressure_label.pack()
accel_label = tk.Label(frame_left, text="Accelerometer:")
accel_label.pack()
gyro_label = tk.Label(frame_left, text="Gyroscope:")
gyro_label.pack()
weather_label = tk.Label(frame_left, text="Weather: N/A")
weather_label.pack()
battery_label = tk.Label(frame_left, text="Battery Level: N/A")
battery_label.pack()
voltage_label = tk.Label(frame_left, text="Voltage: N/A")
voltage_label.pack()
current_label = tk.Label(frame_left, text="Current: N/A")
current_label.pack()
power_label = tk.Label(frame_left, text="Power Consumption: N/A")
power_label.pack()




# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("sdp-422806-11c1654b7049.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open("Satelite_data").sheet1  # Open the first sheet

def update_readings_thread():
    while True:
        try:
            update_readings()
        except Exception as e:
            print(f"Error in updating readings: {e}")
        time.sleep(2)

def read_raw_data(addr):
    high = bus.read_byte_data(address_mpu6050, addr)
    low = bus.read_byte_data(address_mpu6050, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

sending_data = False

def reset_plots():
    global time_data, temp_data, humidity_data
    time_data = []
    temp_data = []
    humidity_data = []
    ax1.clear()
    ax2.clear()
    canvas_plots.draw()

def toggle_sending_data():
    global sending_data
    sending_data = not sending_data
    if sending_data:
        start_button.config(text="Stop Sending Data")
    else:
        start_button.config(text="Start Sending Data")

def detect_weather(temperature_celsius, humidity, pressure):
    if temperature_celsius > 25 and humidity > 70:
        return "Rainy ☂️"
    elif temperature_celsius < 10:
        return "Snowy ❄️"
    elif pressure < 980:
        return "Stormy ⛈️"
    elif pressure > 1020:
        return "Sunny ☀️"
    else:
        return "Clear 🌤️"

def get_battery_level():
    battery_level = 75  # Assume battery level is 75% for demonstration
    return battery_level

def check_battery_level():
    battery_level = get_battery_level()
    battery_label.config(text=f"Battery Level: {battery_level}%")
    if battery_level < 20:
        messagebox.showwarning("Low Battery", f"Attention: Battery level is {battery_level}%. Please charge your device!")
    root.after(60000, check_battery_level)  # Check battery level every minute

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
    gyro_y = read_raw_data(GYRO_YOUT_H) / 131.0
    gyro_z = read_raw_data(GYRO_ZOUT_H) / 131.0

    # Convert temperature to Fahrenheit
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32

    # Update labels with sensor data
    temp_label.config(text=f"Temperature: {temperature_celsius:.2f}°C / {temperature_fahrenheit:.2f}°F")
    humidity_label.config(text=f"Humidity: {humidity:.2f}%")
    pressure_label.config(text=f"Pressure: {pressure:.2f} hPa")
    accel_label.config(text=f"Accelerometer: X={accel_x:.2f}, Y={accel_y:.2f}, Z={accel_z:.2f}")
    gyro_label.config(text=f"Gyroscope: X={gyro_x:.2f}, Y={gyro_y:.2f}, Z={gyro_z:.2f}")
    weather = detect_weather(temperature_celsius, humidity, pressure)
    weather_label.config(text=f"Weather: {weather}")

    # Update battery monitoring
    update_battery_monitoring()

    # Update plots
    update_plots(temperature_celsius, humidity)

    # Update pressure gauge
    update_gauge(pressure)

    # Send data to Google Sheets if sending_data is True

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

# Plotting setup
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
fig.tight_layout()

# Data for plotting
time_data = []
temp_data = []
humidity_data = []

canvas_plots = FigureCanvasTkAgg(fig, master=frame_right)
canvas_plots.get_tk_widget().pack()

map_widget = tkintermapview.TkinterMapView(root, width=1000, height=400, corner_radius=0)
map_widget.place(relx=0.5, rely=0.5,)
map_widget.set_position(3.538979, 103.430239)  # Paris, France
map_widget.set_zoom(15)

def update_plots(temperature, humidity):
    global time_data, temp_data, humidity_data
    
    current_time = time.strftime("%H:%M:%S")
    time_data.append(current_time)
    temp_data.append(temperature)
    humidity_data.append(humidity)

    # Limit data to the last 50 points
    time_data = time_data[-50:]
    temp_data = temp_data[-50:]
    humidity_data = humidity_data[-50:]

    ax1.clear()
    ax2.clear()

    ax1.plot(time_data, temp_data, 'r-')
    ax1.set_title('Temperature over Time')
    ax1.set_ylabel('Temperature (°C)')

    ax2.plot(time_data, humidity_data, 'b-')
    ax2.set_title('Humidity over Time')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_xlabel('Time')

    fig.tight_layout()
    canvas_plots.draw()

def read_voltage():
    # Replace this with the actual code to read voltage from your sensor
    voltage = 3.7  # Example voltage value
    return voltage

def read_current():
    # Replace this with the actual code to read current from your sensor
    current = 1.2  # Example current value in Amps
    return current

def update_battery_monitoring():
    voltage = read_voltage()
    current = read_current()
    power = voltage * current  # Power in Watts

    voltage_label.config(text=f"Voltage: {voltage:.2f} V")
    current_label.config(text=f"Current: {current:.2f} A")
    power_label.config(text=f"Power Consumption: {power:.2f} W")

    root.after(2000, update_battery_monitoring)  # Update every 2 seconds

def update_gauge(pressure):
    gauge_canvas.delete("all")
    center_x = 200
    center_y = 200
    radius = 150

    # Draw the outer circle
    gauge_canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius)

    # Draw the markings
    for i in range(0, 2010, 100):
        angle = (i / 2000) * 180  # Scale to 180 degrees
        x_start = center_x + (radius - 20) * math.cos(math.radians(180 - angle))
        y_start = center_y - (radius - 20) * math.sin(math.radians(180 - angle))
        x_end = center_x + radius * math.cos(math.radians(180 - angle))
        y_end = center_y - radius * math.sin(math.radians(180 - angle))
        gauge_canvas.create_line(x_start, y_start, x_end, y_end, width=2)
        gauge_canvas.create_text(x_end, y_end, text=str(i), font=("Helvetica", 8), anchor=tk.SW)

    # Draw the needle
    angle = (pressure / 2000) * 180  # Scale to 180 degrees
    x_needle = center_x + (radius - 20) * math.cos(math.radians(180 - angle))
    y_needle = center_y - (radius - 20) * math.sin(math.radians(180 - angle))
    gauge_canvas.create_line(center_x, center_y, x_needle, y_needle, fill="red", width=2)

    # Draw the center circle
    gauge_canvas.create_oval(center_x - 10, center_y - 10, center_x + 10, center_y + 10, fill="black")

# Button to start/stop sending data
start_button = tk.Button(frame_left, text="Start Storing Data", command=toggle_sending_data)
start_button.pack()

# Button to reset plots
reset_button = tk.Button(frame_left, text="Reset Data", command=reset_plots)
reset_button.pack()

# Start updating sensor readings and drawing the indicator
update_readings()
draw_indicator()
check_battery_level()
threading.Thread(target=update_readings_thread, daemon=True).start()

# Start the Tkinter main loop
root.mainloop()

