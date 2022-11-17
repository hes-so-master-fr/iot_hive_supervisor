from pycoproc_1 import Pycoproc
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,PRESSURE

def get_temp_hum():
    si = SI7006A20(Pycoproc(Pycoproc.PYSENSE))
    return si

def get_light():
    lt = LTR329ALS01(Pycoproc(Pycoproc.PYSENSE))
    return lt

def get_pressure_alt():
    mp = MPL3115A2(Pycoproc(Pycoproc.PYSENSE),mode=PRESSURE)
    return mp.pressure()

def pysense_read_data():
    si = get_temp_hum()
    return [si.temperature(), get_pressure_alt() ,si.humidity()]