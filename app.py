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
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.core import IncrementalThreadedResourceLoader
#from pygame_functions import *
import pygame_textinput


# os.putenv('SDL_VIDEODRIVER', 'fbcon')   # Display on piTFT
# os.putenv('SDL_FBDEV', '/dev/fb1')     
# os.putenv('SDL_MOUSEDRV', 'TSLIB')     # Track mouse clicks on piTFT
# os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
pygame.init()
pygame.mouse.set_visible(False)

proc = 0
todo_text = '<font face=fira_code size=2 color=#000000><b>To-Do</b>'+'<br><br>'
todo_more = '5725 Lab and project' +'<br><br>'+'research'
WHITE = 255, 255, 255
BLACK = 0,0,0
RED=255,0,0

green = (0, 255, 0) 
blue = (0, 0, 128) 
screen_size = (320,240)
screen = pygame.display.set_mode(screen_size)
my_font= pygame.font.Font("COMIC.TTF", 13)
my_font1 = pygame.font.Font(None,30)
my_buttons= { 'quit':(80,210), 'system':(240,210)}

start = time.time()
weather_position = [(30,30),(85,25),(120,25)]
background_surface = pygame.Surface(screen_size)
background_surface.fill(pygame.Color("#000000"))

loader = IncrementalThreadedResourceLoader()
clock = pygame.time.Clock()
ui_manager = UIManager(screen_size, 'data/themes/theme_1.json', resource_loader=loader)
ui_manager.add_font_paths("Montserrat",
						  "data/fonts/Montserrat-Regular.ttf",
						  "data/fonts/Montserrat-Bold.ttf",
						  "data/fonts/Montserrat-Italic.ttf",
						  "data/fonts/Montserrat-BoldItalic.ttf")

ui_manager.preload_fonts([{'name': 'Montserrat', 'html_size': 4.5, 'style': 'bold'},
						  {'name': 'Montserrat', 'html_size': 4.5, 'style': 'regular'},
						  {'name': 'Montserrat', 'html_size': 2, 'style': 'regular'},
						  {'name': 'Montserrat', 'html_size': 2, 'style': 'italic'},
						  {'name': 'Montserrat', 'html_size': 6, 'style': 'bold'},
						  {'name': 'Montserrat', 'html_size': 6, 'style': 'regular'},
						  {'name': 'Montserrat', 'html_size': 6, 'style': 'bold_italic'},
						  {'name': 'Montserrat', 'html_size': 4, 'style': 'bold'},
						  {'name': 'Montserrat', 'html_size': 4, 'style': 'regular'},
						  {'name': 'Montserrat', 'html_size': 4, 'style': 'italic'},
						  {'name': 'fira_code', 'html_size': 2, 'style': 'regular'},
						  {'name': 'fira_code', 'html_size': 2, 'style': 'bold'},
						  {'name': 'fira_code', 'html_size': 2, 'style': 'bold_italic'}
						  ])
loader.start()
finished_loading = False
while not finished_loading:
	finished_loading, progress = loader.update()

# initialize parameters 
flag = True
portofolio = 0
stocks = {'msft':3,'aapl':2,'amzn':1,'nflx':3}
stockprices = {'msft':'','aapl':'','amzn':'','nflx':''}
counter = 0
inits = [0,10]
inits1 = [200,10]

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
	api = 'https://api.openweathermap.org/data/2.5/onecall?lat=42.44&lon=-76.5&appid=818eb27f395ca0f860e5ce34fedade0f'
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
def stock_price(stock_name):
	price = get_live_price(stock_name)
	
	return str(price)[:6]
	
stock_buttons = {'add':(80,210), 'prev':(140,210),'next':(200,210), 'main':(260,210)}
def stock_menu():
	rich = True
	pluscenter = [(250,80),(250,130),(250,180)]
	minuscenter = [(290,80),(290,130),(290,180)]
	stockcenter = [(50,80),(50,130),(50,180)]
	sharecenter = [(170,80),(170,130),(170,180)]
	pricecenter = [(120,80),(120,130),(120,180)]
	stockpointer = 0

	changes = True
	
	while rich:
		screen.fill(BLACK)
		
		
		if changes:
			all_stocks = []
			for stock in stocks:
				all_stocks.append(stock)
			portofolio = 0
			for items in stocks:
				stockprices[items] = stock_price(items)
				portofolio += float(stockprices[items]) * stocks[items]
			changes = False
		text = my_font1.render('Portofolio: ', True, green)
		textRect = text.get_rect(center=(60,10))  
		screen.blit(text, textRect)
		text = my_font.render(str(portofolio)[:9], True, WHITE)
		textRect = text.get_rect(center=(190,10))  
		screen.blit(text, textRect)
		text = my_font.render('Watchlist ', True, RED)
		textRect = text.get_rect(center=(50,40))  
		screen.blit(text, textRect)
		text = my_font.render('Price ', True, WHITE)
		textRect = text.get_rect(center=(120,40))  
		screen.blit(text, textRect)
		text = my_font.render('Shares ', True, WHITE)
		textRect = text.get_rect(center=(170,40))  
		screen.blit(text, textRect)
		
		for i in range(0,3):
			text = my_font1.render(' + ', True, WHITE)
			textRect = text.get_rect(center=pluscenter[i])  
			screen.blit(text, textRect)
		for i in range(0,3):
			text = my_font1.render(' - ', True, WHITE)
			textRect = text.get_rect(center=minuscenter[i])  
			screen.blit(text, textRect)
		i = 0
		current_stocks = all_stocks[stockpointer:stockpointer+3]
		for stock in current_stocks:
			text = my_font.render(stock, True, WHITE)
			textRect = text.get_rect(center=stockcenter[i])  
			screen.blit(text, textRect)
			text = my_font.render(str(stocks[stock]), True, WHITE)
			textRect = text.get_rect(center=sharecenter[i])  
			screen.blit(text, textRect)
			text = my_font.render(stockprices[stock], True, WHITE)
			textRect = text.get_rect(center=pricecenter[i])  
			screen.blit(text, textRect)
			i += 1
		for my_text, text_pos in stock_buttons.items():    
			text_surface = my_font.render(my_text, True, WHITE)    
			rect = text_surface.get_rect(center=text_pos)
			screen.blit(text_surface, rect) 
		
		for event in pygame.event.get():                
			if(event.type is MOUSEBUTTONUP):
				# Erase the Work space            
				pos = pygame.mouse.get_pos() 
				x,y = pos
				# go to the next level if pressed button.
				if y > 200:                
					if x >250:    
						rich = False
						break
					elif x >190:
						stockpointer += 3
					elif x >130:
						stockpointer -= 3
					else:
						add_stock()
						changes = True
				elif 170<y<190:
					if 280 <x< 300:
						stocks[current_stocks[2]] -= 1
						changes =True
					elif 240<x<260:
						stocks[current_stocks[2]] += 1
						changes = True
				elif 120<y<140 :
					if 280 <x< 300:
						stocks[current_stocks[1]] -= 1
						changes = True
					elif 240<x<260:
						stocks[current_stocks[1]] += 1
						changes = True
				elif 70<y<90 :
					if 280 <x< 300:
						stocks[current_stocks[0]] -= 1
						changes = True
					elif 240<x<260:
						stocks[current_stocks[0]] += 1
						changes = True
		pygame.display.flip()	

def add_stock():
	global stocks
	global stockprices
	textinput = pygame_textinput.TextInput()
	clock = pygame.time.Clock()
	todoflag = True
	while todoflag:
		screen.fill((225, 225, 225))

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				exit()
				

		# Feed it with events every frame
		if textinput.update(events):
			toadd = textinput.get_text().split()
			stocks[toadd[0]] = int(toadd[1])
			
			
			todoflag = False
		# Blit its surface onto the screen
		screen.blit(textinput.get_surface(), (10, 10))

		pygame.display.update()
		clock.tick(30)
	
	

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
	weather = future_weather()
	screen = pygame.display.set_mode((320, 240))
	background = pygame.Surface((320, 240))
	background.fill(pygame.Color('#000000'))

	weeklist = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
	weeklistnum = {'Mon':0, 'Tue':1,'Wed':2,'Thu':3,'Fri':4,'Sat':5,'Sun':6}
	date = display_date()
	today = weeklistnum[str(date[0])]
	# print this week's weather
	daycounter = 0
	weathercounter = 0
	weekdaycenters = [(30,15),(30,50),(30,85),(30,120),(30,155),(30,190),(30,225)]
	weathercenters = [(90,0),(90,35),(90,70),(90,105),(90,140),(90,175),(90,210)]
	tempcenters = [(230,15),(230,50),(230,85),(230,120),(230,155),(230,190),(230,225)]
	for item in weeklist[today:]:
		text = my_font1.render(item, True, green)
		textRect = text.get_rect(center=weekdaycenters[daycounter])  
		screen.blit(text, textRect)
		if 'Rain' in weather[weathercounter] : 
			ball = pygame.image.load("Rain.png")	
		elif 'Sunny' in weather[weathercounter]:
			ball = pygame.image.load("sun.png")
		elif 'Wind' in weather[weathercounter]:
			ball = pygame.image.load("Wind.png")
		elif 'now' in weather[weathercounter]:
			ball = pygame.image.load("Snow.png")
		elif 'louds' in weather[weathercounter]:
			ball = pygame.image.load("Cloud.png")
		elif 'unde' in weather[weathercounter]:
			ball = pygame.image.load("Thunder.png")
		else:
			ball = my_font1.render(str(weather[weathercounter]), True, green)
		ballrect = ball.get_rect()
		ballrect = ballrect.move(weathercenters[daycounter])	
		screen.blit(ball, ballrect)
		weathercounter +=1
		text = my_font1.render(str(weather[weathercounter]), True, green)
		textRect = text.get_rect(center=tempcenters[daycounter])  
		screen.blit(text, textRect)
		weathercounter +=1
		daycounter +=1
	for item in weeklist[:today]:
		text = my_font1.render(item, True, green)
		textRect = text.get_rect(center=weekdaycenters[daycounter])  
		screen.blit(text, textRect)
		if 'Rain' in weather[weathercounter] : 
			ball = pygame.image.load("Rain.png")	
		elif 'Sunny' in weather[weathercounter]:
			ball = pygame.image.load("sun.png")
		elif 'Wind' in weather[weathercounter]:
			ball = pygame.image.load("Wind.png")
		elif 'now' in weather[weathercounter]:
			ball = pygame.image.load("Snow.png")
		elif 'louds' in weather[weathercounter]:
			ball = pygame.image.load("Cloud.png")
		elif 'unde' in weather[weathercounter]:
			ball = pygame.image.load("Thunder.png")
		else:
			ball = my_font1.render(str(weather[weathercounter]), True, green)
		ballrect = ball.get_rect()
		ballrect = ballrect.move(weathercenters[daycounter])	
		screen.blit(ball, ballrect)
		weathercounter +=1
		text = my_font1.render(str(weather[weathercounter]), True, green)
		textRect = text.get_rect(center=tempcenters[daycounter])  
		screen.blit(text, textRect)
		weathercounter +=1
		daycounter +=1
		
	
	pygame.display.flip()
	time.sleep(5)
		
def Todo_menu():
	global todo_more
	textinput = pygame_textinput.TextInput()
	clock = pygame.time.Clock()
	todoflag = True
	while todoflag:
		screen.fill((225, 225, 225))

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				exit()
				

		# Feed it with events every frame
		if textinput.update(events):
			todo_more = textinput.get_text()
			print(todo_more)
			todoflag = False
		# Blit its surface onto the screen
		screen.blit(textinput.get_surface(), (10, 10))

		pygame.display.update()
		clock.tick(30)
	
	
	
# refresh the stock info
refresh = True

while flag:  
	screen.fill(BLACK)
	screen.blit(background_surface, (0, 0))
	
	ui_manager.draw_ui(screen)
	#======================================================
	#
	#======================================================
	# display date and time
	
	
	date = display_date()
	# display a moon if its late in the night 
	if int(str(date[3][:2])) >= 21:
		ball1 = pygame.image.load("moon.png")
		ballrect1 = ball1.get_rect()
		ballrect1 = ballrect1.move(inits1)
		screen.blit(ball1, ballrect1)
	text = my_font1.render(str(date[3]), True, RED)
	textRect = text.get_rect(center=(250,30))  
	screen.blit(text, textRect)
	text = my_font1.render(str(date[0]), True, green)
	textRect = text.get_rect(center=(190,30))  
	screen.blit(text, textRect)
	text = my_font.render(str(date[1]), True, WHITE)
	textRect = text.get_rect(center=(200,50))  
	screen.blit(text, textRect)
	text = my_font.render(str(date[2]), True, WHITE)
	textRect = text.get_rect(center=(225,50))  
	screen.blit(text, textRect)
	text = my_font.render(str(date[4]), True, WHITE)
	textRect = text.get_rect(center=(260,50))  
	screen.blit(text, textRect)
	


	#======================================================
	# display functions   
	for my_text, text_pos in my_buttons.items():    
		text_surface = my_font.render(my_text, True, WHITE)    
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect) 

	#=======================================================
	#display weather
	#update frequency: every 10 minutes
	if counter == 0 or counter % 6000 == 0:
		weather = current_weather()
	if 'Rain' in weather[0] : 
		ball = pygame.image.load("Rain.png")
		ballrect = ball.get_rect()
		ballrect = ballrect.move(inits)
		
	elif 'Sunny' in weather[0] or 'lear' in weather[0]:
		ball = pygame.image.load("sun.png")
		ballrect = ball.get_rect()
		ballrect = ballrect.move(inits)
	elif 'Wind' in weather[0]:
		ball = pygame.image.load("Wind.png")
		ballrect = ball.get_rect()
		ballrect = ballrect.move(inits)
	elif 'now' in weather[0]:
		ball = pygame.image.load("Snow.png")
		ballrect = ball.get_rect()
		ballrect = ballrect.move(inits)
	elif 'louds' in weather[0]:
		ball = pygame.image.load("Cloud.png")
		ballrect = ball.get_rect()
		ballrect = ballrect.move(inits)
	elif 'unde' in weather[0]:
		ball = pygame.image.load("Thunder.png")
		ballrect = ball.get_rect()
		ballrect = ballrect.move(inits)
	else:
		text = my_font1.render(str(weather[0]), True, green)
		textRect = text.get_rect(center=weather_position[0])  
		screen.blit(text, textRect)
	screen.blit(ball, ballrect)
	
	for i in range(1,3):
		text = my_font.render(str(weather[i]), True, WHITE)
		textRect = text.get_rect(center=weather_position[i])  
		screen.blit(text, textRect)
	#==================================================
	#display room temperature
	#update frequency: every 10 minutes	
	if counter == 0 or counter % 6000 == 0:
		temp_data = room_temp()
	temp = 'room temp: '+ str(temp_data) + '°C'
	text = my_font.render(temp, True, WHITE)
	textRect = text.get_rect(center=(60,60))  
	screen.blit(text, textRect)
	#=======================================================
	#print To-do list 

	htm_text_block_2 = UITextBox(todo_text+todo_more,
							 pygame.Rect((150, 70), (140, 130)),
							 manager=ui_manager,
							 object_id="#text_box_2")
	#=======================================================
	# print your portofolio
	#update every 10 minutes
	if counter == 0 or counter % 6000 == 0 or refresh:
		portofolio = 0
		if stocks:
			for items in stocks:
				price = stock_price(items)
				portofolio += float(price) * stocks[items]
		refresh = False
	text = my_font1.render('Portofolio: ', True, green)
	textRect = text.get_rect(center=(60,130))  
	screen.blit(text, textRect)
	text = my_font.render(str(portofolio)[:9], True, WHITE)
	textRect = text.get_rect(center=(60,160))  
	screen.blit(text, textRect)
	#======================================================
	# Detect touch on screen to determine next move
	for event in pygame.event.get():                
		if(event.type is MOUSEBUTTONUP):
			# Erase the Work space            
			pos = pygame.mouse.get_pos() 
			x,y = pos
			# go to the next level if pressed button.
			if y > 200:                
				if x < 160:    
					print ('quit button pressed')
					flag = False
					break
				else:
					function_menu()
			elif y < 40 and x < 110 :
				weather_menu()
			elif 70 < y < 150 and  100 < x < 250:
				Todo_menu()
			elif 120< y < 190 and 0 <x <130:
				stock_menu()
				refresh = True
	if(not time.time() - start < 300):
		flag = False
	pygame.display.flip() 
	#update counter every 0.1 second. Refresh counter every hour.
	time.sleep(0.1)
	counter += 1
	if counter > 36000:
		counter = 0

