import smbus
import time
import RPi.GPIO as GPIO 
bus = smbus.SMBus(1)
GPIO.setmode(GPIO.BCM) 
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
# I2C address and register addresses

IMU1_addr = 0x6a
IMU2_addr = 0x6b
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
FIFO_STATUS2 = 0x3B
FIFO_DATA_OUT_TAG = 0x78
FIFO_CTRL1 = 0x07
INT2 = 0x0E

#bit patterns

#INT1 
INT1_DRDY_XL = 0x01

#INT2
INT2_DRDY_XL = 0x01
INT2_FIFO_TH = 0x08
INT2_FIFO_FULL = 0x20

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

#FIFO_CTRL1

#CTRL3_C
BOOT = 0x80
SW_RESET = 0x01

#FIFO_STATUS2
FIFO_FULL_IA = 0x20

	
# put in power down mode
bus.write_byte_data(IMU1_addr,CTRL1,0x00)
# reset and reboot the IMU
bus.write_byte_data(IMU1_addr,CTRL3_C,SW_RESET|BOOT)

bus.write_byte_data(IMU2_addr,CTRL1,0x00)
# reset and reboot the IMU
bus.write_byte_data(IMU2_addr,CTRL3_C,SW_RESET|BOOT)
time.sleep(0.001)

# 1st IMU Accelerometor data on INT1
#bus.write_byte_data(IMU1_addr,INT1,INT1_DRDY_XL)
# 1st IMU set Accelerometor data rate 104 Hz
bus.write_byte_data(IMU2_addr,CTRL1,ODR_XL2)


# accelerometer data write into FIFO at 104 Hz
bus.write_byte_data(IMU2_addr,FIFO_CTRL3,BDR_XL2)
# set FIFO in FIFO mode.
bus.write_byte_data(IMU2_addr,FIFO_CTRL4,FIFO_MODE0)






# 1st IMU sensor hub data-ready signal on INT1
#bus.write_byte_data(IMU_addr,MD1_CFG,INT1_SHUB)
# INT2 rising on FIFO watermark
bus.write_byte_data(IMU2_addr,INT1,INT2_FIFO_FULL)




# start the I2C between IMU 


def my_callback(channel): 
	
	def check():
		print('entered checking function')
		status3 = bus.read_byte_data(IMU2_addr,FIFO_STATUS1)
		print(status3)
		status1 = bus.read_byte_data(IMU2_addr,FIFO_STATUS2)
		print(status1)

		if (status1 & FIFO_FULL_IA):
			count = 0
			print('1st IMU is full')
			while (count <=128 ) :
				# read the tag and 6 continous byte FIFO data
				IMU = bus.read_i2c_block_data(IMU2_addr,FIFO_DATA_OUT_TAG,28)
				print(IMU)
				count += 1
			count = 0
			print('read 512 1st IMU data')
			if GPIO.input(24):
				print('the signal is still high after read 1st IMU')
				check()
		
	if GPIO.input(24):
		print('pin high')
	print('interrupt received')
	check()
	print('exit ISR')
		
'''		
		if IMU2[6] != 255 and IMU2[6] != 253:
			
			if IMU2[0] == 17 or  IMU2[0] == 18 or  IMU2[0] == 20 or  IMU2[0] == 23 :
				data1_count +=1
			elif IMU2[0] == 113 or  IMU2[0] == 114 or  IMU2[0] == 116 or  IMU2[0] == 119 :
				data2_count +=1
	data1_count=0
	data2_count=0
'''
	
GPIO.add_event_detect(24, GPIO.RISING, callback=my_callback) 

try:  
    print("Waiting for rising edge on port 24")  
    time.sleep(60) 
     
  
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit  
