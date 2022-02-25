import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

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
