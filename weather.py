import requests

api = 'http://api.openweathermap.org/data/2.5/weather?zip=14850,us&appid=818eb27f395ca0f860e5ce34fedade0f'
data = requests.get(api).json()
weather = data['weather'][0]['main']
print(weather)
temp = data['main']['temp']-273.15
print(str(temp)[:5]+ 'C')
hum = data['main']['humidity']
print(hum)


api = 'https://api.openweathermap.org/data/2.5/onecall?lat=-76.5&lon=42.44&appid=818eb27f395ca0f860e5ce34fedade0f'
