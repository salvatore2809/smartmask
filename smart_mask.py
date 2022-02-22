import board
import time
import adafruit_bme680
from adafruit_circuitplayground import cp
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

class Breath:
    def __init__(self):
        self.breaths = 0
        self.breath_period = 0
        self.avg_rpm = 0

        self.last_value_gas = 0
        self.gas_noise = 2000
        self.bufflen = 4
        self.slope_buffer = [0] * self.bufflen
        self.gas_buffer = [0] * 10
        self.rpm = 0
        self.last_time_breath = 0
        self.last_time_event = 0
        self.last_rpm = 0
        self.variance_gas_buffer = 3
        self.debug_mode = False

    def is_breath_detected(self, gas_value, current_time, last_wearing_status):

        print(current_time)
        is_breath_detected = False

        self.new_value_gas = gas_value

        self.slope = self.calculate_slope(self.new_value_gas)
        self.last_value_gas = self.new_value_gas
        self.update_led_status(self.slope, led_pos = 7)

        if self.is_peak_detected(self.slope_buffer):

            current_time_event = current_time
            self.breath_period = current_time_event - self.last_time_event
            self.last_time_event = current_time_event

            if self.bufflen == 4 and self.breath_period < 8 and self.breath_period > 1 and self.variance_gas_buffer > 0.4:
                self.rpm = self.calculate_rpm( self.breath_period )
                self.breath_event_update()
                is_breath_detected = True
                #self.send_breath_report()

            elif self.bufflen == 2 and self.breath_period < 3 and self.breath_period > 0.85 and self.variance_gas_buffer > 0.15:
                self.rpm = self.calculate_rpm( self.breath_period )
                self.breath_event_update()
                is_breath_detected = True
                #self.send_breath_report()
            else:
                if self.debug_mode:
                    print(" undetected variance: {0:.2f} breath period: {2:.2f}".format( self.variance_gas_buffer, self.breath_period))

        self.update_gas_bufflen(last_wearing_status)
        self.update_slope_buffer()
        self.update_gas_buffer()
        self.variance_gas_buffer = self.calculate_variance(self.gas_buffer)
        self.debug()
        return is_breath_detected

    def is_peak_detected(self,slope_buffer):

        if self.bufflen is not None:
            #last 4 or 2 elements of slope_buffer
            buffer = slope_buffer[-self.bufflen:]
            for i in range(self.bufflen/2):
                if buffer[i] >= 0 and buffer[self.bufflen-1-i] < 0:
                    pass
                else:
                    return False
            return True

    def calculate_variance(self, data):
        # Number of observations
        n = len(data)
        # Mean of the data
        mean = sum(data) / n
        # Square deviations
        deviations = [(x - mean) ** 2 for x in data]
        # Variance
        variance = sum(deviations) / n
        return variance
    def calculate_slope(self, new_value_gas):

        value_diff = new_value_gas - self.last_value_gas

        if value_diff != 0:
            if abs(value_diff) < self.gas_noise:
                return 0
            else:
                return (value_diff) / abs(value_diff)
        else:
            return value_diff

    def update_led_status(self, slope, led_pos):

        cp.pixels.brightness = 0.1

        if self.variance_gas_buffer > 0.25:
            if slope > 0 :
                cp.pixels[led_pos] = (0, 255, 0)
            elif slope <= 0 :
                cp.pixels[led_pos] = (255, 0, 0)
        else:
            cp.pixels[led_pos] = (0, 0, 200)
    def calculate_rpm(self,breath_period):
        if breath_period != 0:
            return 60 / breath_period
        else:
            return 0

    def breath_event_update(self):
        self.last_time_breath = self.last_time_event  	
        self.avg_rpm = (self.last_rpm + self.rpm)/2
        self.breaths += 1
        self.last_rpm = self.rpm

    def update_gas_bufflen(self, last_wearing_status):
        if self.avg_rpm <= 35 and self.bufflen == 2 or last_wearing_status is False:
            self.bufflen = 4
        elif self.avg_rpm > 35 and self.bufflen == 4 and self.breath_period < 3:
            self.bufflen = 2

    def update_slope_buffer(self):
        self.slope_buffer.pop(0)
        self.slope_buffer.append(self.slope)
    def update_gas_buffer(self):
        self.gas_buffer.pop(0)
        self.gas_buffer.append(self.new_value_gas/10000)
    def debug(self):
        if self.debug_mode :
            debug_msg = "gas: "+str(self.new_value_gas)+" slope: "+str(self.slope)+" buffer: "+str(self.slope_buffer[-self.bufflen:])+" var: "
            debug_msg += str(self.variance_gas_buffer)+" breaths: "+str(self.breaths)+" breath period: "+str(self.breath_period)+" rpm: "
            debug_msg += str(self.rpm)+" avg_rpm: "+str(self.avg_rpm)+" wearing_status: "+str(self.last_wearing_status)
            print(debug_msg)

class BleInterface:
    def __init__(self):
        self.adv_mode = False
        self.ble = BLERadio()
        self.uart_server = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.uart_server)
    def start_ble_connection(self):
        if not self.ble.connected and self.adv_mode is False:
            self.ble.start_advertising(self.advertisement)
            self.adv_mode = True
        elif self.ble.connected and self.adv_mode is True:
            self.ble.stop_advertising()
            self.ble.stop_scan()
            self.uart_server.write("BLE SERVICE STARTED\n")
            self.adv_mode = False
    def send_breath_report(self, breaths, breath_period, avg_rpm):
        if self.ble.connected:
            self.ble._clean_connection_cache()
            self.uart_server.reset_input_buffer()
            self.uart_server.write(str(self.ble.tx_power)+"\n")
            self.uart_server.write(" n_br: {0}   br_T: {1:.2f}   avg_rpm: {2:.1f}\n".format(breaths,breath_period,avg_rpm))
        print(" n_br: {0}   br_T: {1:.2f}   avg_rpm: {2:.1f}\n".format(breaths, breath_period, avg_rpm))
        #print(" detected breaths: {0} variance: {1:.2f} breath period: {2:.2f} avg rpm: {3:.2f}".format(self.breaths,self.variance_gas_buffer,self.breath_period,self.avg_rpm))
    def send_warning_message(self):
        if self.ble.connected:
            self.uart_server.write("\nWARNING THE MASK IS NOT WORN CORRECTLY,\n")
            self.uart_server.write("PLEASE POSITION IT CORRECTLY\n")

class Sensor:
    sensor_name = ""
    value_unit_of_measure = ""
    get_value_instruction = ""
    number_of_axis = 1
    offset = 0
    current_value = 0
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
    def get_sensor_value(self):
        self.current_value = eval(self.get_value_instruction)
        return self.current_value
    def get_label(self):
        return self.sensor_name + self.value_unit_of_measure
    def get_sensor_value_string(self):
        if self.number_of_axis == 1 :
            return self.format_str.format(self.get_sensor_value() + self.offset)
        if self.number_of_axis == 3 :
            x,y,z = self.get_sensor_value()
            return self.format_str.format(x + self.offset, y + self.offset, z + self.offset)

class Led:

    lastTimeBlink=0
    status=False
    position = 0

    def __init__(self, ledPos, brightness):
        self.lastTimeBlink = 0
        self.position = ledPos
        cp.pixels.brightness = brightness

    def blink(self, delaySec):
        currentTime = time.monotonic()
        if ((currentTime - self.lastTimeBlink) >= delaySec):
            self.lastTimeBlink = time.monotonic()
            if self.status==True:
                #cp.pixels[self.position] = (0, 255, 0)
                self.setColour((0, 255, 0))
            else:
                #cp.pixels[self.position] = (0, 0, 0)
                self.setColour((0, 0, 0))
            self.status = not(self.status)

    def setColour(self, colour = [0, 0, 0]):
        cp.pixels[self.position] = colour


class File:

    lastTimeFile = 0
    samplesMax = 100 #save this number of rows in file, each time
    samples = 0
    fileName = ""
    filePath = ""
    lineToWrite=""
    totalSamples = 0
    is_file_created = False
    rowMaxEachFile = 20000

    def __init__(self, lastTimeFile, fileName, sensor_list):
        self.lastTimeFile = lastTimeFile
        self.sensor_list = sensor_list
        #the code below raise error if partition is not mounted in write
        with open("/file.txt", "w", encoding='utf-8-sig') as fp:
            pass
        self.fileName = fileName

    def createFile(self):
        if "logs" not in os.listdir():
                os.mkdir("/logs")
        for index in range(100):
            self.filePath = "/logs/"+self.fileName+str(index)+".csv"
            if self.filePath[6:] not in os.listdir("/logs/"):
                with open(self.filePath, "w", encoding='utf-8-sig') as fp:
                    fp.seek(0)
                    title=""
                    for sensor in self.sensor_list:
                        title+=sensor.get_label()+';'
                    title+="\n"
                    fp.write(title)
                    fp.flush()
                    fp.close()
                    print(self.filePath)
                    self.is_file_created = True
                return
        raise NameError('too much files in current directory')

    def saveLineToWriteOnFile(self,forceEnd):
        #for excel
        self.lineToWrite = self.lineToWrite.replace('.',',')
        with open(self.filePath, "a") as fp:
            print(self.lineToWrite)
            fp.write(self.lineToWrite)
            fp.flush()
            fp.close()
        self.samples=0
        self.lineToWrite=""
        if forceEnd or self.totalSamples >= self.rowMaxEachFile:
            self.is_file_created = False
            return True
        return False

    def createLineTOWrite(self):
        for sensor in self.sensor_list:
            self.lineToWrite += sensor.get_sensor_value_string()+';'
        self.lineToWrite+="\n"
        self.samples += 1
        self.totalSamples += 1
        return False

    def logSensors(self, delaySec, forceEnd):
        if not self.is_file_created:
            self.createFile()
        if self.samples >= self.samplesMax or forceEnd or self.totalSamples >= self.rowMaxEachFile:
            return self.saveLineToWriteOnFile(forceEnd)
        elif time.monotonic() - self.lastTimeFile >= delaySec :
            self.lastTimeFile = time.monotonic()
            return self.createLineTOWrite()

    def logSensorsNoDelay(self, forceEnd):
        if not self.is_file_created:
            self.createFile()
        if self.samples >= self.samplesMax or forceEnd or self.totalSamples >= self.rowMaxEachFile:
            return self.saveLineToWriteOnFile(forceEnd)
        else:
            return self.createLineTOWrite()


class Smart_mask:

    last_wearing_status = False
    last_breath_monitor_time = 0

    def __init__(self):
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug = False)
        self.bme680.sea_level_pressure = 1017
        self.bme680._min_refresh_time = 0.001
        temperature_offset = 0

        self.user_breath = Breath()
        self.user_ble_interface = BleInterface()


        time_sensor = Sensor("time","s", "time.monotonic()",precision = 3)
        gas_sensor = Sensor("gas","ohm","bme680.gas",precision = 0)
        in_mask_temp_sensor = Sensor("in mask temp","°C","bme680.temperature", offset = temperature_offset,precision = 2)
        in_mask_humidity_sensor = Sensor("in mask hum","%","bme680.relative_humidity",precision = 2)
        pressure_sensor = Sensor("press","hPa","bme680.pressure",precision = 2)
        altitude_sensor = Sensor("altit","m","bme680.altitude",precision = 2)
        microphone_sensor = Sensor("mic","%","cp.sound_level",precision = 0)
        light_sensor = Sensor("light","%","cp.light",precision = 1)
        on_board_temp_sensor = Sensor("ext temp","°C","cp.temperature",precision = 2)
        accelerometer_sensor = Sensor("AccX AccY AccZ","m/s^2","cp.acceleration",number_of_axis = 3,precision = 3)

        self.sensor_list = [time_sensor,gas_sensor, in_mask_temp_sensor, in_mask_humidity_sensor, pressure_sensor,
                            altitude_sensor,microphone_sensor,light_sensor,on_board_temp_sensor,accelerometer_sensor]
        self.recFile = File(time.monotonic(),"sensor_data", self.sensor_list)

    def breath_monitor_service(self, delay):

        current_time = time.monotonic()

        if current_time - self.last_breath_monitor_time > delay :

            last_breath_monitor_time = current_time

            self.user_ble_interface.start_ble_connection()

            if self.user_breath.is_breath_detected(self.bme680.gas, current_time, self.last_wearing_status):
                self.user_ble_interface.send_breath_report( self.user_breath.breaths, self.user_breath.breath_period, self.user_breath.avg_rpm )

            self.update_wearing_status( current_time, self.user_breath.last_time_breath )


    def log_sensors_on_file(self, delay, forcedClosure):
        return self.recFile.logSensorsNoDelay(forcedClosure)

    def update_wearing_status(self, current_time, last_time_breath):
        #la funzione non avvisa se la mascerina parte non indossata
        current_wearing_status = self.is_mask_used(current_time, last_time_breath)
        if self.last_wearing_status != current_wearing_status:
            self.last_wearing_status = current_wearing_status
            if current_wearing_status is False :
                self.user_ble_interface.send_warning_message()
            print("\nWARNING THE MASK IS NOT WORN CORRECTLY,\n")
            print("PLEASE POSITION IT CORRECTLY\n")

    def is_mask_used(self, cur_time, last_time_breath):
        if cur_time - last_time_breath > 40:
            return False
        return True









