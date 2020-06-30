
import smbus
import time
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO 
from matplotlib.animation import FuncAnimation
bus = smbus.SMBus(1)
GPIO.setmode(GPIO.BCM) 

# I2C address and register addresses

IMU_addr = 0x6a
# master SD0 connected to GND
slave_addr_read = 0b11010111
# 0x6b = 1101011
# write |0
# read |1
slave_addr_write=  0b11010110
FUNC_CFG_ACCESS  = 0x01
SLAV = 0x15
SLAVS = 0x16
SLAV_CONF = 0x17
DATAW = 0x21
MASTER_CONFIG = 0x14
STAT = 0x22
INT1 = 0x0D
CTRL1 = 0x10
ACCX = 0x28
ACCXH = 0x29
ACCY = 0x2A
ACCYH = 0x2B
ACCZ = 0x2C
ACCZH = 0x2D
STAT_REG = 0x1E
MASTER_MAIN = 0x39
SENSOR_1 = 0x02
FIFO_CTRL3 = 0x09
FIFO_CTRL4 = 0x0A
CTRL3_C = 0x12
CTRL6_C = 0x15
CTRL9_XL = 0x18
CRTL1_XL = 0x10
MD1_CFG = 0x5E
FIFO_STATUS1 = 0x3A
FIFO_DATA_OUT_TAG = 0x78
INT2 = 0x0E

#bit patterns

#INT1 
INT1_DRDY_XL = 0x01

#INT2
INT2_DRDY_XL = 0x01

#CTRL1_XL
ODR_XL3 = 0x80
ODR_XL2 = 0x40
ODR_XL1 = 0x20
ODR_XL0 = 0x10

#FIFO_CTRL3
BDR_XL3 = 0x08
BDR_XL2 = 0x04
BDR_XL1 = 0x02
BDR_XL0 = 0x01

#FIFO_CTRL4

FIFO_MODE2 = 0x04
FIFO_MODE1 = 0x02
FIFO_MODE0 = 0x01


#MD1_CFG 

INT1_SHUB = 0x01

#FUNC_CFG_ACCESS

SHUB_REG_ACCESS = 0x40


#SLAV0_CONFIG
BATCH_EXT_SENS_0_EN = 0x08
Slave0_numop2 = 0x04
Slave0_numop1 = 0x02
Slave0_numop0 = 0x01

#MASTER_CONFIG
WRITE_ONCE = 0x40
START_CONFIG = 0x20
SHUB_PU_EN = 0x08
MASTER_ON  = 0x04
AUX_SENS_ON1 = 0x02
AUX_SENS_ON0 = 0x01

#CTRL3_C
BOOT = 0x80
SW_RESET = 0x01

def one_shot_write(register, value):
	bus.write_byte_data(IMU_addr,FUNC_CFG_ACCESS,SHUB_REG_ACCESS)
	bus.write_byte_data(IMU_addr,SLAV,slave_addr_write)
	bus.write_byte_data(IMU_addr,SLAVS,register)
	bus.write_byte_data(IMU_addr,SLAV_CONF,0x00)
	bus.write_byte_data(IMU_addr,DATAW,value)
	bus.write_byte_data(IMU_addr,MASTER_CONFIG,WRITE_ONCE|SHUB_PU_EN|MASTER_ON)
	while (not bus.read_byte_data(IMU_addr,STAT)>>7):
		continue
	bus.write_byte_data(IMU_addr,MASTER_CONFIG,SHUB_PU_EN)
	time.sleep(0.0003)
	bus.write_byte_data(IMU_addr,FUNC_CFG_ACCESS,0x00)

def one_shot_read():
	bus.write_byte_data(IMU_addr,FUNC_CFG_ACCESS,SHUB_REG_ACCESS)
	bus.write_byte_data(IMU_addr,SLAV,slave_addr_read)
	bus.write_byte_data(IMU_addr,SLAVS,ACCX)
	# 2nd IMU data is store in FIFO at 104 HZ, 6 BYTE read
	bus.write_byte_data(IMU_addr,SLAV_CONF,BATCH_EXT_SENS_0_EN|Slave0_numop2|Slave0_numop1)
	#Use INT2 pin as sensorhub data-ready, using external trigger
	#bus.write_byte_data(IMU_addr,MASTER_CONFIG,WRITE_ONCE|START_CONFIG|SHUB_PU_EN|MASTER_ON)
	bus.write_byte_data(IMU_addr,MASTER_CONFIG,WRITE_ONCE|SHUB_PU_EN|MASTER_ON)
	bus.write_byte_data(IMU_addr,FUNC_CFG_ACCESS,0x00)

# put in power down mode
bus.write_byte_data(IMU_addr,CTRL1,0x00)
# reset and reboot the IMU
bus.write_byte_data(IMU_addr,CTRL3_C,SW_RESET|BOOT)
time.sleep(0.1)

# Running the reset of 2nd IMU would cause the program stuck
#one_shot_write(CTRL1,0x00)
#one_shot_write(CTRL3_C,SW_RESET|BOOT)
#time.sleep(0.1)

registerdata = bus.read_word_data(IMU_addr,CTRL3_C)
print('registerdata in CTRL3 is:' + str(registerdata))
# 1st IMU Accelerometor data on INT1
bus.write_byte_data(IMU_addr,INT1,INT1_DRDY_XL)
# 1st IMU set Accelerometor data rate 104 Hz
bus.write_byte_data(IMU_addr,CTRL1,ODR_XL2)

# one shot write to INT1 on 2nd IMU 
# 2nd IMU Accelerometor data on INT1
one_shot_write(INT1,INT1_DRDY_XL)

# One shot write to CTRL1 on 2nd IMU 
# 2nd IMU set Accelerometor data rate 104 Hz
one_shot_write(CTRL1,ODR_XL2)

# accelerometer data write into FIFO at 104 Hz
bus.write_byte_data(IMU_addr,FIFO_CTRL3,BDR_XL2)
# set FIFO in FIFO mode.
bus.write_byte_data(IMU_addr,FIFO_CTRL4,FIFO_MODE0)

# 1st IMU sensor hub data-ready signal on INT1
#bus.write_byte_data(IMU_addr,MD1_CFG,INT1_SHUB)


def read_data(register):
	accx = bus.read_word_data(IMU_addr,register)
	return accx


# start the I2C between IMU 
one_shot_read()

data1_count = 0
data2_count = 0
x1_axis = []
x2_axis = []
Z1_vals = []
Z2_vals = []
Z1_lowpass = [0,0,0,0,0,0,0,0,0,0]
Z2_lowpass = [0,0,0,0,0,0,0,0,0,0]
X1_vals = []
X2_vals = []
X1_lowpass = [0,0,0,0,0,0,0,0,0,0]
X2_lowpass = [0,0,0,0,0,0,0,0,0,0]
Y1_vals = []
Y2_vals = []
Y1_lowpass = [0,0,0,0,0,0,0,0,0,0]
Y2_lowpass = [0,0,0,0,0,0,0,0,0,0]
def animate(i):
	count = 1
	level = 1
	#f= open("output.txt","w+")
	global data1_count
	global data2_count
	level = bus.read_byte_data(IMU_addr,FIFO_STATUS1)
	print(level)
	#while ( level != 0 or count <= 104) :
	while (data2_count <= 104) :
		#read the FIFO level
		level = bus.read_byte_data(IMU_addr,FIFO_STATUS1)
		print(level)
		# read the tag and 6 continous byte FIFO data
		if level != 0:
			IMU2 = bus.read_i2c_block_data(IMU_addr,FIFO_DATA_OUT_TAG,7)
			print(IMU2)
			count += 1
			
			if IMU2[6] != 255 and IMU2[6] != 253:
				if IMU2[0] == 17 or  IMU2[0] == 18 or  IMU2[0] == 20 or  IMU2[0] == 23 :
					data1_count +=1
				elif IMU2[0] == 113 or  IMU2[0] == 114 or  IMU2[0] == 116 or  IMU2[0] == 119 :
					data2_count +=1
					if data2_count == 1: #start using external trigger at 20th 2nd IMU data
						bus.write_byte_data(IMU_addr,FUNC_CFG_ACCESS,SHUB_REG_ACCESS)
						bus.write_byte_data(IMU_addr,MASTER_CONFIG,WRITE_ONCE|START_CONFIG|SHUB_PU_EN|MASTER_ON)
						bus.write_byte_data(IMU_addr,FUNC_CFG_ACCESS,0x00)




		
animate(1)

