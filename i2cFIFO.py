
import smbus
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
bus = smbus.SMBus(1)

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
CTRL6_C = 0x15
CTRL9_XL = 0x18
CRTL1_XL = 0x10
MD1_CFG = 0x5E
FIFO_STATUS1 = 0x3A
FIFO_DATA_OUT_TAG = 0x78

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
SHUB_PU_EN = 0x08
MASTER_ON  = 0x04
AUX_SENS_ON1 = 0x02
AUX_SENS_ON0 = 0x01

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
	# 2nd IMU data is store in FIFO at 104 HZ
	bus.write_byte_data(IMU_addr,SLAV_CONF,BATCH_EXT_SENS_0_EN|Slave0_numop2|Slave0_numop1)
	bus.write_byte_data(IMU_addr,MASTER_CONFIG,WRITE_ONCE|SHUB_PU_EN|MASTER_ON)
	bus.write_byte_data(IMU_addr,FUNC_CFG_ACCESS,0x00)
	
	
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
# set FIFO in continuous mode.
bus.write_byte_data(IMU_addr,FIFO_CTRL4,FIFO_MODE2|FIFO_MODE1)

# 1st IMU sensor hub data-ready signal on INT1
bus.write_byte_data(IMU_addr,MD1_CFG,INT1_SHUB)

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
	while ( level != 0 or count <= 104) :
		#read the FIFO level
		level = bus.read_byte_data(IMU_addr,FIFO_STATUS1)
		print(level)
		# read the tag and 6 continous byte FIFO data
		IMU2 = bus.read_i2c_block_data(IMU_addr,FIFO_DATA_OUT_TAG,7)
		print(IMU2)
		
		if IMU2[6] != 255 and IMU2[6] != 253:
			if len(hex(IMU2[5])) == 3:
				z_data = int(hex(IMU2[6])[2:]+'0'+ hex(IMU2[5])[2:],16)
			else:
				z_data = int(hex(IMU2[6])[2:]+ hex(IMU2[5])[2:],16)
			if z_data < 32768:
				z_data = z_data / 16391
			else:
				z_data = (z_data - 65535) / 16391
			if len(hex(IMU2[1])) == 3:
				x_data = int(hex(IMU2[2])[2:]+ '0'+ hex(IMU2[1])[2:],16)
			else:
				x_data = int(hex(IMU2[2])[2:]+ hex(IMU2[1])[2:],16)
			
			if x_data < 32768:
				x_data = x_data / 16391
			else:
				x_data = (x_data - 65535) / 16391
			if len(hex(IMU2[3])) == 3:
				y_data = int(hex(IMU2[4])[2:]+'0'+ hex(IMU2[3])[2:],16)
			else:
				y_data = int(hex(IMU2[4])[2:]+ hex(IMU2[3])[2:],16)
			
			if y_data < 32768:
				y_data = y_data / 16391
			else:
				y_data = (y_data - 65535) / 16391
			print(str(x_data) + ' ' + str(y_data) + ' ' + str(z_data))
			if IMU2[0] == 17 or  IMU2[0] == 18 or  IMU2[0] == 20 or  IMU2[0] == 23 :
				Z1_lowpass.pop(0)
				Z1_lowpass.append(z_data)
				data = sum(Z1_lowpass) / 10
				Z1_vals.append(data)
				X1_lowpass.pop(0)
				X1_lowpass.append(x_data)
				data = sum(X1_lowpass) / 10
				X1_vals.append(data)
				Y1_lowpass.pop(0)
				Y1_lowpass.append(y_data)
				data = sum(Y1_lowpass) / 10
				Y1_vals.append(data)
				x1_axis.append(data1_count)
				data1_count +=1
			elif IMU2[0] == 113 or  IMU2[0] == 114 or  IMU2[0] == 116 or  IMU2[0] == 119 :
				
				Z2_lowpass.pop(0)
				Z2_lowpass.append(z_data)
				data = sum(Z2_lowpass) / 10
				Z2_vals.append(data)
				X2_lowpass.pop(0)
				X2_lowpass.append(x_data)
				data = sum(X2_lowpass) / 10
				X2_vals.append(data)
				Y2_lowpass.pop(0)
				Y2_lowpass.append(y_data)
				data = sum(Y2_lowpass) / 10
				Y2_vals.append(data)
				x2_axis.append(data2_count)
				data2_count +=1
			count +=1
	plt.cla()
	plt.subplot(231)
	plt.plot(x1_axis,X1_vals,label = 'IMU1 X')
	plt.title('IMU1 X')
	plt.subplot(232)
	plt.plot(x1_axis,Y1_vals,label = 'IMU1 Y')
	plt.title('IMU1 Y')

	plt.subplot(233)
	plt.plot(x1_axis,Z1_vals,label = 'IMU1 Z')
	plt.title('IMU1 Z')

	plt.subplot(234)
	plt.plot(x2_axis,X2_vals,label = 'IMU2 X')
	plt.title('IMU2 X')

	plt.subplot(235)
	plt.plot(x2_axis,Y2_vals,label = 'IMU2 Y')
	plt.title('IMU2 Y')

	plt.subplot(236)
	plt.plot(x2_axis,Z2_vals,label = 'IMU2 Z')
	plt.title('IMU2 Z')
	#plt.legend(loc='upper left')
	#plt.tight_layout()
		
ani = FuncAnimation(plt.gcf(),animate,interval=1000)

plt.tight_layout()
plt.show()

#f.close()

