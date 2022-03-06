#import adafruit_bme680
import board
from adafruit_circuitplayground import cp
import time
import busio
uart = busio.UART(board.TX, board.RX, baudrate=115200)

class Sensor:
    last_read_time = 0
    sensor_name = ""
    value_unit_of_measure = ""
    get_value_instruction = ""
    number_of_axis = 1
    offset = 0
    current_value = 0
    #bme680 sensor values
    temp=0
    press=0
    gas=0
    hum=0
    def __init__(self,sensor_name, um, get_value_instruction, number_of_axis = 1, offset = 0, precision = 2):
        self.sensor_name = sensor_name
        self.value_unit_of_measure ='[' + um + ']'
        self.get_value_instruction = get_value_instruction
        self.number_of_axis = number_of_axis
        self.offset = offset
        self.value_precision = str(precision)
        if self.number_of_axis == 1 :
            self.format_str = str("{:."+ self.value_precision +"f}")
        if self.number_of_axis == 3 :
            self.format_str = str("{0:."+self.value_precision+"f}; {1:."+self.value_precision+"f}; {2:."+self.value_precision+"f}")

    def read_bme680(self):

        end_reading = False
        str_received=""
        #print()
        while not end_reading:
            #try:
            data = uart.read(1)  # read a byte
            if data is not None:  # Data was received
                str_received+=data.decode()
                if data.decode()=='\n' and len(str_received)>4:
                    str_num=""
                    number=0
                    #print(str_received)
                    for char in str_received:
                        if char.isdigit() or char=='.':
                            str_num+=char
                    #print(str_num, end=' ')
                    number=float(str_num)
                    if "gas" in str_received:
                        self.gas = number*1000
                        #print(str(time.monotonic())+" "+str(gas))
                        #print(" gas "+str(self.gas),end=' ')
                    if "hum" in str_received:
                        self.hum = number
                        #print(" hum "+str(self.hum),end=' ')
                        #print(str(time.monotonic())+" "+str(gas))
                        end_reading=True
                    if "press" in str_received:
                        self.press = number
                        #print(" press "+str(self.press),end=' ')
                        #print(str(time.monotonic())+" "+str(gas))
                    if "temp" in str_received:
                        self.temp = number
                        #print(" temp "+str(self.temp),end='\n')
                        #print(str(time.monotonic())+" "+str(gas))
                    str_received=""
            #except:
            #    print("unable to read bme680")
            #    end_reading=True

    def get_sensor_value(self):
        #try:
        if True:
            current_time = time.monotonic()
            if self.sensor_name == ("gas" or "in_mask_temp" or "in_mask_humidity" or "pressure") :
                if (current_time-self.last_read_time) > 0.30:
                    self.read_bme680()
                    self.last_read_time = time.monotonic()
                else:
                    if self.sensor_name == "gas":
                        self.current_value = self.gas
                    if self.sensor_name == "in_mask_temp":
                        self.current_value = self.temp
                    if self.sensor_name == "in_mask_humidity":
                        self.current_value = self.hum
                    if self.sensor_name == "pressure":
                        self.current_value = self.press
            else:
                self.current_value = eval(self.get_value_instruction)
        #except:
        #    print("unable to get value from sensor: " + self.sensor_name)
        return self.current_value

    def get_label(self):
        return self.sensor_name + self.value_unit_of_measure

    def get_sensor_value_string(self):
        if self.number_of_axis == 1 :
            return self.format_str.format(self.get_sensor_value() + self.offset)
        if self.number_of_axis == 3 :
            x,y,z = self.get_sensor_value()
            return self.format_str.format(x + self.offset, y + self.offset, z + self.offset)
