#!/usr/bin/env python3

'''
 Copyright (c) 2022 University of Applied Sciences Western Switzerland / MSE

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.

 Project: HES-SO Master / IoT 

 Purpose: 

 Author:  Julien Piguet
 Date:    November 2022
'''


from network import LoRa
import socket
import time
import ubinascii
import pycom
from machine import I2C
import bme280_float as bme280
from array import array
import pysense_sensors

pycom.heartbeat(False)

# Config
control = 0
interval = 300
is_pysense = True

# Initialise LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
# app_eui = ubinascii.unhexlify('70B3D5499F79F82C')
app_eui = LoRa().mac()
app_key = ubinascii.unhexlify('B3963FDB9001CDB49EB5C41408917999')
# dev_eui = ubinascii.unhexlify('70B3D57ED0056E95')
dev_eui = LoRa().mac()

# Initialise I2C
bme = None
if not is_pysense:
    i2c = I2C(0, pins=('P23','P22')) 
    bme = bme280.BME280(i2c=i2c)

def measure_data():
    data = pysense_sensors.pysense_read_data() if is_pysense else bme.read_compensated_data()
    print("({:.2f}C, {:.2f}hPa, {:.2f}%)".format(data[0],data[1]/100,data[2]))
    temp = int(data[0]*100)
    pressure = int(data[1])
    humidity = int(data[2]*100)
    return [temp, pressure, humidity]

def lora_join(attempts: int = 10): 
    lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)
    current_attempts = 0
    while not lora.has_joined():
        if current_attempts == attempts:
            raise Exception('Join Error', 'Abort joining after {current_attempts} tries')
        time.sleep(2.5)
        print('Not yet joined...')
        current_attempts+=1
    print('Joined')
    
def create_socket():
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    return s

def send_to_lora(socket, data_bytes):
    socket.setblocking(True)
    socket.send(bytes(data_bytes))
    socket.setblocking(False)
    
def receive_data(socket):
    data = socket.recv(64)
    print(data)
    
def send_mesure(control_byte: int, data: list[int]):
    try:
        lora_join()
        socket = create_socket()
        send_to_lora(socket,control_byte.to_bytes(1, 'big') + data[0].to_bytes(4, 'big') + data[1].to_bytes(4, 'big')+data[2].to_bytes(4, 'big'))
        receive_data(socket)
        
    except Exception as e:
        print(e)

def main():
    while(True):
        pycom.rgbled(0xFF0000)
        data = measure_data()
        pycom.rgbled(0x0000FF)
        send_mesure(control, data)
        pycom.rgbled(0x000000)
        print("Wait 300 secondes")
        time.sleep(interval)

if __name__ == "__main__":
    main()