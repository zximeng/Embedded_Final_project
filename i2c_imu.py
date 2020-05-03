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


bus.write_byte_data(0x6a,FIFO_CTRL3,0x04)
# enable acc reading at 104 Hz

bus.write_byte_data(0x6a,FIFO_CTRL4,0x06)
# set fifo in continuous mode 

bus.write_byte_data(0x6a,0x5E,0x01)
# enable sensor hub data-ready on INT1

bus.write_byte_data(0x6a,CTRL6_C,0x80)
# INT2 input mode

#bus.write_byte_data(0x6a,CTRL9_XL,0xE8)
#extend DEN 






# read from sensor hub


bus.write_byte_data(0x6a,FUNC,0x40)
bus.write_byte_data(0x6a,SLAV,slave_addr_read)
bus.write_byte_data(0x6a,SLAVS,ACCX)
bus.write_byte_data(0x6a,SLAV_CONF,0x0E)
bus.write_byte_data(0x6a,MAST,0x4C)
bus.write_byte_data(0x6a,FUNC,0x00)
accx = bus.read_word_data(0x6a,0x29) # clear data ready on OUTX_H_A
# poll data ready on status_reg
while (not bus.read_byte_data(0x6a,STAT_REG) & 0x01):
	continue
while (not bus.read_byte_data(0x6a,MASTER_MAIN) & 0x01):
	continue
bus.write_byte_data(0x6a,FUNC,0x40)
bus.write_byte_data(0x6a,MAST,0x08)

	



#get level and do 10 read from fifo

level = bus.read_byte_data(0x6a,0x3A)
print(level)
count = 3
while (level or count) :
	
	IMU2 = bus.read_i2c_block_data(0x6a,0x78,7)
	print(IMU2)
	if IMU2[0] != 17 and  IMU2[0] != 18 and  IMU2[0] != 20 and  IMU2[0] != 23 :
		print(IMU2)
	else:
		print('no luck')
	count -= 1
	

