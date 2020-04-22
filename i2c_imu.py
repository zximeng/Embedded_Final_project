
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
STAT_REG = 0x1E
MASTER_MAIN = 0x39
SENSOR_1 = 0x02

# slave SD0 connected to VDD

# First initialize the master device, then use the sensor hub to
# initialize the slave device. Read from the slave device, save to FIFO, read 
# from master device and read from FIFO. 
bus.write_byte_data(0x6a,INT1,0x01)
bus.write_byte_data(0x6a,CTRL1,0x40)

# one shot write to INT1 on slave IMU 
bus.write_byte_data(0x6a,FUNC,0x40)
bus.write_byte_data(0x6a,SLAV,slave_addr_write)
bus.write_byte_data(0x6a,SLAVS,INT1)
bus.write_byte_data(0x6a,SLAV_CONF,0x00)
bus.write_byte_data(0x6a,DATAW,0x01)
bus.write_byte_data(0x6a,MAST,0x4C)
while (not bus.read_byte_data(0x6a,STAT)>>7):
	continue
bus.write_byte_data(0x6a,MAST,0x08)
time.sleep(0.0003)
bus.write_byte_data(0x6a,FUNC,0x00)

# One shot write to CTRL
bus.write_byte_data(0x6a,FUNC,0x40)
bus.write_byte_data(0x6a,SLAV,slave_addr_write)
bus.write_byte_data(0x6a,SLAVS,CTRL1)
bus.write_byte_data(0x6a,SLAV_CONF,0x00)
bus.write_byte_data(0x6a,DATAW,0x60)
bus.write_byte_data(0x6a,MAST,0x4C)
while (not bus.read_byte_data(0x6a,STAT)>>7):
	continue
bus.write_byte_data(0x6a,MAST,0x08)
time.sleep(0.0003)
bus.write_byte_data(0x6a,FUNC,0x00)

print('the data from the second IMU:')
# One shot read from 2nd IMU 
bus.write_byte_data(0x6a,FUNC,0x40)
bus.write_byte_data(0x6a,SLAV,slave_addr_read)
bus.write_byte_data(0x6a,SLAVS,ACCX)
bus.write_byte_data(0x6a,SLAV_CONF,0x01)
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
time.sleep(0.0003)
accx = bus.read_word_data(0x6a,SENSOR_1)
print(accx)
bus.write_byte_data(0x6a,FUNC,0x00)

def read_data():
	accx = bus.read_word_data(0x6a,ACCX)
	return accx
print('the data from the first IMU:')


for i in range(0,10):
	print(read_data())
	time.sleep(1)
	
