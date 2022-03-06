import board
import time
#import adafruit_bme680
from adafruit_circuitplayground import cp
import breath as br
import ble_interface as ble_int
import sensor as sensor
import filemanager as fileman
#
class Smart_mask:
    temperature_offset = 0
    last_value_gas=0
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

    accel_buff = [(0,0,0)] * 10
    variance_buff =[0]*20
    last_sum_xyz = 0
    last_acc_event_time = 0
    def __init__(self, names_sensor_to_rec):
        '''
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug = False)
        self.bme680.sea_level_pressure = 1017
        #self.bme680._min_refresh_time = 0.001
        '''

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

        for sensor in self.sensor_list:
            if sensor.sensor_name=="gas":
                gas = sensor.get_sensor_value()

        if (current_time - self.last_breath_monitor_time) >= delay :
        #if gas != self.last_value_gas:
        #if (current_time - self.last_breath_monitor_time) >= delay :
            self.last_breath_monitor_time = current_time
            self.last_value_gas = gas
            self.user_ble_interface.start_ble_connection()
            #print(gas)
            #bug the execution stops at bme680.gas after sending ble message
            if self.is_mask_worn():
                if self.user_breath.is_breath_detected(gas, current_time, self.last_wearing_status):
                    self.user_ble_interface.send_breath_report( self.user_breath.breaths, self.user_breath.breath_period, self.user_breath.avg_rpm )

            self.update_wearing_status( current_time, self.user_breath.last_time_breath )


    def is_mask_worn(self):
        for sensor in self.sensor_list:
            if sensor.sensor_name=="accelerometer_XYZ":
                xyz = sensor.get_sensor_value()
        #current_sum_xyz = abs(xyz.x) + abs(xyz.y) + abs(xyz.z)

        #diff = current_sum_xyz - self.last_sum_xyz
        #print(diff)
        self.accel_buff.pop(0)
        self.accel_buff.append((xyz.x, xyz.y, xyz.z))
        variance_x = self.calculate_variance([a_tuple[0] for a_tuple in self.accel_buff])
        variance_y = self.calculate_variance([a_tuple[1] for a_tuple in self.accel_buff])
        variance_z = self.calculate_variance([a_tuple[2] for a_tuple in self.accel_buff])
        self.variance_buff.pop(0)
        self.variance_buff.append(sum([variance_x,variance_y,variance_z]))

        if self.calculate_variance(self.variance_buff)*100000 > 100:
            self.last_acc_event_time = self.last_breath_monitor_time
        if (self.last_breath_monitor_time-self.last_acc_event_time) > 10:
            return False
        return True
        #print(self.calculate_variance(self.variance_buff)*100000)
        #print(sum([variance_x,variance_y,variance_z]))
        #avg_variance_buff = sum(self.variance_buff)/20

        #print(variance_accel)
        #print(avg_variance_buff )
        #return avg_variance_buff > 0.02
        #self.last_sum_xyz = current_sum_xyz

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
