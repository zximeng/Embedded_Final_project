import pygame     # Import pygame graphics library
import time
import request
import smbus
import requests



def current_weather():
	api = 'http://api.openweathermap.org/data/2.5/weather?zip=14850,us&appid=818eb27f395ca0f860e5ce34fedade0f'
	data = requests.get(api).json()
	weather = data['weather'][0]['main']
	temp_raw = data['main']['temp']-273.15
	temp = str(temp_raw)[:5]+ 'C'
	hum = data['main']['humidity']
	
def future_weather():
	api = 'https://api.openweathermap.org/data/2.5/onecall?lat=-76.5&lon=42.44&appid=818eb27f395ca0f860e5ce34fedade0f'
	data = requests.get(api).json()
	for i in range(0,7):
		weather = data['daily'][i]['weather'][0]['main']
		print(i)
		temp = data['daily'][i]['temp']['day']
		print(weather)
		print(temp)
	
def display_date():
	currenttime = str(time.ctime()).split(' ')
def display_portfolio():
	

def room_temp():
	bus = smbus.SMBus(1)
	addr = 0x48
	roomtemp = bus.read_byte(addr)


pygame.init()
pygame.mouse.set_visible(False)
WHITE = 255, 255, 255
BLACK = 0,0,0
RED=255,0,0

green = (0, 255, 0) 
blue = (0, 0, 128) 
screen = pygame.display.set_mode((320, 240))
my_font= pygame.font.Font(None, 24)
