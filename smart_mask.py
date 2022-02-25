import board
import time
import adafruit_bme680
from adafruit_circuitplayground import cp
import breath as br
import ble_interface as ble_int
import sensor as sensor
import filemanager as fileman

class Smart_mask:

    last_wearing_status = False
    last_breath_monitor_time = 0

    def __init__(self):

        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug = False)
        self.bme680.sea_level_pressure = 1017
        self.bme680._min_refresh_time = 0.001
        temperature_offset = 0

        self.user_breath = br.Breath()
        self.user_ble_interface = ble_int.BleInterface()


        time_sensor = sensor.Sensor("time","s", "time.monotonic()",precision = 3)
        gas_sensor = sensor.Sensor("gas","ohm","bme680.gas",precision = 0)
        in_mask_temp_sensor = sensor.Sensor("in mask temp","°C","bme680.temperature", offset = temperature_offset,precision = 2)
        in_mask_humidity_sensor = sensor.Sensor("in mask hum","%","bme680.relative_humidity",precision = 2)
        pressure_sensor = sensor.Sensor("press","hPa","bme680.pressure",precision = 2)
        altitude_sensor = sensor.Sensor("altit","m","bme680.altitude",precision = 2)
        microphone_sensor = sensor.Sensor("mic","%","cp.sound_level",precision = 0)
        light_sensor = sensor.Sensor("light","%","cp.light",precision = 1)
        on_board_temp_sensor = sensor.Sensor("ext temp","°C","cp.temperature",precision = 2)
        accelerometer_sensor = sensor.Sensor("AccX AccY AccZ","m/s^2","cp.acceleration",number_of_axis = 3,precision = 3)

        self.sensor_list = [time_sensor,gas_sensor, in_mask_temp_sensor, in_mask_humidity_sensor, pressure_sensor,
                            altitude_sensor,microphone_sensor,light_sensor,on_board_temp_sensor,accelerometer_sensor]
        #self.recFile = fileman.File(time.monotonic(),"sensor_data", self.sensor_list)

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









