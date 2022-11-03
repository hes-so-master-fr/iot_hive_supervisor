from network import LoRa
import socket
import time
import ubinascii
import machine
import pycom


#import for fetching data from sensors
from pycoproc_1 import Pycoproc
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
#from pycoproc import Pycoproc

# create an OTAA authentication parameters, change them to the provided credentials
app_eui = ubinascii.unhexlify('70B3D54997A0DDE4')
app_key = ubinascii.unhexlify('0C6A1E3E1857D8855FBA2CF04492AC6A')
#uncomment to use LoRaWAN application provided dev_eui
dev_eui = ubinascii.unhexlify('70B3D57ED0056E96')

#-------------------------------------------------------------- network mgmt -------------------------------------------------------------------

class Dataload:
    def _init_(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp
        self.temp
        self.hum
        self.light
        self.alt
        self.press
        self.serialized

    def update(self, py):
        si = get_temp_hum(py)
        self.temp = si.temperature()
        self.hum = si.humidity()
        lt = get_light(py)
        self.light = lt.light()
        press, alt = get_pressure_alt(py)
        self.press = press
        self.alt = alt

    def serialize_data(self):
        self.serialized = bytes([self.temp,self.hum, self.press,self.light,self.alt])
        #self.serialized = bytes([0x01])

    def send(self, sock):
        #self.serialize()
        send_data(sock, self.serialized)

# connect to lora
def connect_lora(dev_eui, app_eui, app_key):
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')

    print('Joined')

    return lora

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
def open_socket():
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

    return s



def send_data(socket, data):
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    socket.setblocking(True)
    socket.send(data)
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    socket.setblocking(False)



def receive_data():
    data = s.recv(64)

    if data == NULL:
        data = -1
    else:
        print(data)
    return data

##----------------------------------------------------------------------------- sensor fetching ---------------------------------------------

def get_temp_hum(py):
    si = SI7006A20(py)
    print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")
    print("Dew point: "+ str(si.dew_point()) + " deg C")
    t_ambient = 24.4
    print("Humidity Ambient for " + str(t_ambient) + " deg C is " + str(si.humid_ambient(t_ambient)) + "%RH")

    return si


def get_light(py):
    lt = LTR329ALS01(py)
    print("Light (channel Blue lux, channel Red lux): " + str(lt.light()))
    return lt

def get_pressure_alt(py):

    mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
    print("MPL3115A2 temperature: " + str(mp.temperature()))
    print("Altitude: " + str(mp.altitude()))
    mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
    print("Pressure: " + str(mpp.pressure()))
    alt = mp.altitude()
    pressure = mpp.pressure()

    return alt, pressure

##------------------------------------------------------------------------------- exec -------------------------------------------------------

lora = connect_lora(dev_eui, app_eui, app_key)
sock = open_socket()


dt = Dataload("payload", 0)
py = Pycoproc(Pycoproc.PYSENSE)

#while True:
dt.update(py)
dt.serialize_data()
dt.send(sock)
