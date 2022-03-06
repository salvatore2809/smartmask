import time
from adafruit_circuitplayground import cp
'''
to do list:
'''
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


    def smoother(self, gas_value):

        self.update_gas_buffer(gas_value)
        smoothval = int(sum(self.gas_buffer[-3:])/3)
        return smoothval

    def update_gas_buffer(self, gas_value):
        self.gas_buffer.pop(0)
        self.gas_buffer.append(gas_value/10000)

    def is_breath_detected(self, gas_value, current_time, last_wearing_status):

        #print(current_time)
        is_breath_detected = False

        #self.new_value_gas = self.smoother(gas_value)
        self.new_value_gas = int(gas_value)
        #print((self.new_value_gas,self.new_value_gas))
        self.slope = self.calculate_slope(self.new_value_gas)
        self.last_value_gas = self.new_value_gas
        self.update_led_status(self.slope, led_pos = 7)

        if self.is_peak_detected(self.slope_buffer):

            current_time_event = current_time
            self.breath_period = current_time_event - self.last_time_event
            self.last_time_event = current_time_event

            if self.bufflen == 4 and self.breath_period < 8 and self.breath_period > 1: #and self.variance_gas_buffer > 0.4:
                self.rpm = self.calculate_rpm( self.breath_period )
                self.breath_event_update()
                is_breath_detected = True

            elif self.bufflen == 2 and self.breath_period < 3 and self.breath_period > 0.85: #and self.variance_gas_buffer > 0.2:
                self.rpm = self.calculate_rpm( self.breath_period )
                self.breath_event_update()
                is_breath_detected = True
                #self.send_breath_report()
            else:
                if self.debug_mode:
                    print(" undetected variance: {0:.2f} breath period: {2:.2f}".format( self.variance_gas_buffer, self.breath_period))

        #print(self.variance_gas_buffer)
        #print(self.slope_buffer)
        self.update_gas_bufflen(last_wearing_status)
        self.update_slope_buffer()
        self.update_gas_buffer(self.new_value_gas)
        self.variance_gas_buffer = self.calculate_variance(self.gas_buffer)
        self.debug()
        return is_breath_detected

    def is_peak_detected(self,slope_buffer):

        if self.bufflen is not None:
            #last 4 or 2 elements of slope_buffer
            buffer = slope_buffer[-self.bufflen:]
            print(buffer)
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
        #print(value_diff)
        if value_diff != 0:
            if abs(value_diff) < self.gas_noise:
                return 0
            else:
                return (value_diff) / abs(value_diff)
        else:
            return value_diff

    def update_led_status(self, slope, led_pos):

        cp.pixels.brightness = 0.1

        #if self.variance_gas_buffer > 0.5:
        if True:
            if slope >= 0 :
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

    def update_gas_buffer(self, gas_value):
        self.gas_buffer.pop(0)
        self.gas_buffer.append(gas_value/10000)

    def debug(self):
        if self.debug_mode :
            debug_msg = "gas: "+str(self.new_value_gas)+" slope: "+str(self.slope)+" buffer: "+str(self.slope_buffer[-self.bufflen:])+" var: "
            debug_msg += str(self.variance_gas_buffer)+" breaths: "+str(self.breaths)+" breath period: "+str(self.breath_period)+" rpm: "
            debug_msg += str(self.rpm)+" avg_rpm: "+str(self.avg_rpm)+" wearing_status: "+str(self.last_wearing_status)
            print(debug_msg)
