from imu import MPU6050
from time import sleep
from machine import Pin, I2C





i2c =I2C( 1, sda=Pin(2),scl=Pin(3),freq=100000)
imu =MPU6050(i2c)

try:
    
    file = open("data.txt","a")
    
    
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
    
    print("\tax", ax, "\tay", ay ,"\taz", az ,"\tgx",gx,"\tgy",gy,"\tgz",gz,"\tTemperature", tem)
    
    file.write(str(count)+","+str(ax)+","+str(ay)+","+str(az)+","+str(gx)+","+str(gy)+","+str(gz)+","+str(tem)+"\n")
    file.flush()
    count+=1
    
    sleep(1)

