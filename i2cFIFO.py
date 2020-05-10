
import smbus
import time
bus = smbus.SMBus(1)
addr = 0x6a
# master SD0 connected to GND
slave_addr_read = 0b11010111
# 0x6b = 1101011
# write |0
# read |1
slave_addr_write=  0b11010110
FUNC = 0x01
SLAV = 0x15
SLAVS = 0x16
SLAV_CONF = 0x17
DATAW = 0x21
MAST = 0x14
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


def one_shot_write(register, value):
	bus.write_byte_data(0x6a,FUNC,0x40)
	bus.write_byte_data(0x6a,SLAV,slave_addr_write)
	bus.write_byte_data(0x6a,SLAVS,register)
	bus.write_byte_data(0x6a,SLAV_CONF,0x00)
	bus.write_byte_data(0x6a,DATAW,value)
	bus.write_byte_data(0x6a,MAST,0x4C)
	while (not bus.read_byte_data(0x6a,STAT)>>7):
		continue
	bus.write_byte_data(0x6a,MAST,0x08)
	time.sleep(0.0003)
	bus.write_byte_data(0x6a,FUNC,0x00)

def one_shot_read():
	bus.write_byte_data(0x6a,FUNC,0x40)
	bus.write_byte_data(0x6a,SLAV,slave_addr_read)
	bus.write_byte_data(0x6a,SLAVS,ACCX)
	bus.write_byte_data(0x6a,SLAV_CONF,0x0E)
	bus.write_byte_data(0x6a,MAST,0x4C)
	bus.write_byte_data(0x6a,FUNC,0x00)
	
	

bus.write_byte_data(0x6a,INT1,0x01)
bus.write_byte_data(0x6a,CTRL1,0x40)

# one shot write to INT1 on slave IMU 
one_shot_write(INT1,0x01)

# One shot write to CTRL
one_shot_write(CTRL1,0x60)

bus.write_byte_data(0x6a,FIFO_CTRL3,0x04)

bus.write_byte_data(0x6a,FIFO_CTRL4,0x06)
bus.write_byte_data(0x6a,0x5E,0x01)

def read_data(register):
	accx = bus.read_word_data(0x6a,register)
	return accx



one_shot_read()


count = 700
while ( count) :
	level = bus.read_byte_data(0x6a,0x3A)
	print(level)
	IMU2 = bus.read_i2c_block_data(0x6a,0x78,7)
	print(IMU2)
	if IMU2[0] == 17 or  IMU2[0] == 18 or  IMU2[0] == 20 or  IMU2[0] == 23 :
		print('fount the great treasure')

	count -=1


