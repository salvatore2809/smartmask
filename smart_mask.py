import board
import time
import adafruit_bme680
from adafruit_circuitplayground import cp
import breath as br
import ble_interface as ble_int
import sensor as sensor
import filemanager as fileman
#
class Smart_mask:
    temperature_offset = 0
    last_wearing_status = False
    last_breath_monitor_time = time.monotonic()

    time_sensor = sensor.Sensor("time","s", "time.monotonic()",precision = 3)
    gas_sensor = sensor.Sensor("gas","ohm","bme680.gas",precision = 0)
    in_mask_temp_sensor = sensor.Sensor("in_mask_temp","°C","bme680.temperature", offset = temperature_offset,precision = 2)
    in_mask_humidity_sensor = sensor.Sensor("in_mask_humidity","%","bme680.relative_humidity",precision = 2)
    pressure_sensor = sensor.Sensor("pressure","hPa","bme680.pressure",precision = 2)
    altitude_sensor = sensor.Sensor("altitude","m","bme680.altitude",precision = 2)
    microphone_sensor = sensor.Sensor("microphone","%","cp.sound_level",precision = 0)
    light_sensor = sensor.Sensor("light","%","cp.light",precision = 1)
    on_board_temp_sensor = sensor.Sensor("board_temp","°C","cp.temperature",precision = 2)
    accelerometer_sensor = sensor.Sensor("accelerometer_XYZ","m/s^2","cp.acceleration",number_of_axis = 3,precision = 3)


    all_sensor_list = [time_sensor,gas_sensor, in_mask_temp_sensor, in_mask_humidity_sensor, pressure_sensor,
                        altitude_sensor,microphone_sensor,light_sensor,on_board_temp_sensor,accelerometer_sensor]
    sensor_list=[]
    def __init__(self, names_sensor_to_rec):

        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug = False)
        self.bme680.sea_level_pressure = 1017
        #self.bme680._min_refresh_time = 0.001


        self.user_breath = br.Breath()
        self.user_ble_interface = ble_int.BleInterface()

        for sensor_name in names_sensor_to_rec:
            for sensor in self.all_sensor_list:
                if sensor_name == sensor.sensor_name:
                    self.sensor_list.append(sensor)
                    self.all_sensor_list.remove(sensor)

        print("Added this sensors to record list:")
        for sensor in self.sensor_list:
            print(sensor.sensor_name, end = ' , ')
        print("")
        #self.sensor_list = [time_sensor,gas_sensor, in_mask_temp_sensor, in_mask_humidity_sensor, pressure_sensor,
        #                    altitude_sensor,microphone_sensor,light_sensor,on_board_temp_sensor,accelerometer_sensor]
        #self.recFile = fileman.File(time.monotonic(),"sensor_data", self.sensor_list)

    def breath_monitor_service(self, delay):

        current_time = time.monotonic()

        if (current_time - self.last_breath_monitor_time) >= delay :

            self.last_breath_monitor_time = current_time

            self.user_ble_interface.start_ble_connection()

            #bug the execution stops at bme680.gas after sending ble message
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
