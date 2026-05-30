#!/home/weijun/iot_lab/env/bin/python3
import board
import adafruit_dht

# Initialise the dht device, with data pin connected to GPIO 4:
dhtDevice = adafruit_dht.DHT11(board.D4)

# To read values:
temperature = dhtDevice.temperature
humidity = dhtDevice.humidity

print(f"Temp: {temperature} C, Humidity: {humidity}%")
