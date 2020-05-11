# -*- coding: utf-8 -*-
import pygame     # Import pygame graphics library
import time
import requests
import smbus
import requests
import pygame_gui
import os
from pygame.locals import *   # for event MOUSE variables
from yahoo_fin.stock_info import *
import subprocess
proc = 0

def current_weather():
	api = 'http://api.openweathermap.org/data/2.5/weather?zip=14850,us&appid=818eb27f395ca0f860e5ce34fedade0f'
	data = requests.get(api).json()
	weather = data['weather'][0]['main']
	temp_raw = data['main']['temp']-273.15
	temp = str(temp_raw)[:4]+ '°C'
	hum = data['main']['humidity']
	weather_info = [weather,temp,hum]
	return weather_info
	
def future_weather():
	api = 'https://api.openweathermap.org/data/2.5/onecall?lat=-76.5&lon=42.44&appid=818eb27f395ca0f860e5ce34fedade0f'
	data = requests.get(api).json()
	weather_info = []
	for i in range(0,7):
		weather = data['daily'][i]['weather'][0]['main']
		weather_info.append(weather)
		temp_raw = data['daily'][i]['temp']['day'] - 273.15
		temp = str(temp_raw)[:4]+ '°C'
		weather_info.append(temp)
	print(weather_info)
	return weather_info 
		
	
def display_date():
	currenttime = str(time.ctime()).split(' ')
	return currenttime
def display_portfolio():
	print('portofolio')

def room_temp():
	global room_temperature
	bus = smbus.SMBus(1)
	addr = 0x48
	roomtemp = bus.read_byte(addr)
	room = roomtemp
	return room
	
	
def function_menu():
	global proc
	window_surface = pygame.display.set_mode((320, 240))
	background = pygame.Surface((320, 240))
	background.fill(pygame.Color('#000000'))
	manager = pygame_gui.UIManager((320, 240))
	button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (60, 30)),
                                                text='Main',
                                                manager=manager)
	button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((95, 10), (60, 30)),
                                                text='Reboot',
                                                manager=manager)
	button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 50), (80, 40)),
                                                text='Shutdown',
                                                manager=manager)
	button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 100), (100, 40)),
                                                text='Camera On',
                                                manager=manager)
	button5 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 150), (100, 40)),
                                                text='Camera Off',
                                                manager=manager)
                        
	clock = pygame.time.Clock()
	is_running = True

	while is_running:

		time_delta = clock.tick(60)/1000.0
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				is_running = False

			if event.type == pygame.USEREVENT:
				if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
					if event.ui_element == button1:
						is_running = False
					elif event.ui_element == button2:
						os.system('sudo reboot')
					elif event.ui_element == button3:
						os.system('sudo shutdown')
					elif event.ui_element == button4:
						proc = subprocess.Popen(['python3','videostream.py'])
					elif event.ui_element == button5:
						proc.terminate()
			manager.process_events(event)
		
		manager.update(time_delta)
		window_surface.blit(background, (0, 0))
		manager.draw_ui(window_surface)

		pygame.display.update()

def weather_menu():
	weatehr = future_weather()



pygame.init()
pygame.mouse.set_visible(False)
WHITE = 255, 255, 255
BLACK = 0,0,0
RED=255,0,0

green = (0, 255, 0) 
blue = (0, 0, 128) 
screen = pygame.display.set_mode((320, 240))
my_font= pygame.font.Font(None, 20)
my_font1 = pygame.font.Font(None,30)
my_buttons= { 'quit':(80,180), 'system':(240,180)}
start = time.time()
weather_position = [(30,30),(85,25),(120,25)]

flag = True
while flag:  
	screen.fill(BLACK) 
	# display date and time
	date = display_date() 
	text = my_font1.render(str(date[4]), True, RED)
	textRect = text.get_rect(center=(250,30))  
	screen.blit(text, textRect)
	text = my_font1.render(str(date[0]), True, green)
	textRect = text.get_rect(center=(190,30))  
	screen.blit(text, textRect)
	text = my_font.render(str(date[1]), True, WHITE)
	textRect = text.get_rect(center=(200,50))  
	screen.blit(text, textRect)
	text = my_font.render(str(date[3]), True, WHITE)
	textRect = text.get_rect(center=(225,50))  
	screen.blit(text, textRect)
	for event in pygame.event.get():        
		if(event.type is MOUSEBUTTONDOWN): 
			pos = pygame.mouse.get_pos()           
		elif(event.type is MOUSEBUTTONUP):
			# Erase the Work space 
			# display functions   
			for my_text, text_pos in my_buttons.items():    
				text_surface = my_font.render(my_text, True, WHITE)    
				rect = text_surface.get_rect(center=text_pos)
				screen.blit(text_surface, rect)            
			pos = pygame.mouse.get_pos() 
			x,y = pos
			#display weather
			weather = current_weather()
			text = my_font1.render(str(weather[0]), True, green)
			textRect = text.get_rect(center=weather_position[0])  
			screen.blit(text, textRect)
			for i in range(1,3):
				text = my_font.render(str(weather[i]), True, WHITE)
				textRect = text.get_rect(center=weather_position[i])  
				screen.blit(text, textRect)
			#display room temperature
			
			temp_data = room_temp()
			print(temp_data)
			temp = 'room temp: '+ str(temp_data) + '°C'
			text = my_font.render(temp, True, WHITE)
			textRect = text.get_rect(center=(60,60))  
			screen.blit(text, textRect)
			pygame.display.flip()       
			if y > 170:                
				if x < 160:    
					print ('quit button pressed')
					flag = False
				else:
					function_menu()
			elif y < 40 and x < 110 :
				weather_menu()
	if(not time.time() - start < 300):
		flag = False
