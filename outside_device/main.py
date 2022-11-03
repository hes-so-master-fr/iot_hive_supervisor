from network import LoRa
import socket
import time
import ubinascii
import machine
import pycom

#from pycoproc import Pycoproc

# create an OTAA authentication parameters, change them to the provided credentials
app_eui = ubinascii.unhexlify('70B3D54997A0DDE4')
app_key = ubinascii.unhexlify('0C6A1E3E1857D8855FBA2CF04492AC6A')
#uncomment to use LoRaWAN application provided dev_eui
dev_eui = ubinascii.unhexlify('70B3D57ED0056E96')


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



lora = connect_lora(dev_eui, app_eui, app_key)
sock = open_socket()
data = byte([0x01, 0x02, 0x03])
send_data(sock, data)
